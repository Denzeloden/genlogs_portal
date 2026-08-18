import { useEffect, useState } from "react";
import { searchRoutes } from "./api/client";
import CarrierList from "./components/CarrierList";
import RouteMaps from "./components/RouteMaps";
import SearchForm from "./components/SearchForm";
import ThemeToggle from "./components/ThemeToggle";

const THEME_STORAGE_KEY = "genlogs-theme";

function getInitialTheme() {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return "dark";
}

export default function App() {
  const [theme, setTheme] = useState(getInitialTheme);
  const [fromCity, setFromCity] = useState("New York City");
  const [toCity, setToCity] = useState("Washington DC");
  const [carriers, setCarriers] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [carrierStatus, setCarrierStatus] = useState("idle");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);

    const themeColor = theme === "dark" ? "#0f142e" : "#f5f7fb";
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", themeColor);
  }, [theme]);

  function toggleTheme() {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  }

  async function handleSearch() {
    setLoading(true);
    setError("");

    try {
      const result = await searchRoutes(fromCity, toCity);
      setCarriers(result.carriers);
      setRoutes(result.routes);
      setCarrierStatus(result.carriers.length ? "results" : "empty");
    } catch (searchError) {
      setCarriers([]);
      setRoutes([]);
      setCarrierStatus("idle");
      setError("Unable to complete the search. Check that the backend is running.");
      console.error(searchError);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
      </header>
      <SearchForm
        fromCity={fromCity}
        toCity={toCity}
        onFromChange={setFromCity}
        onToChange={setToCity}
        onSearch={handleSearch}
        loading={loading}
      />
      {error ? <p className="error-banner">{error}</p> : null}
      <RouteMaps routes={routes} />
      <CarrierList carriers={carriers} status={carrierStatus} />
    </main>
  );
}
