import { useEffect, useState } from "react";
import { searchRoutes, SearchRequestError } from "./api/client";
import CarrierList from "./components/CarrierList";
import RouteMaps from "./components/RouteMaps";
import SearchForm from "./components/SearchForm";
import ThemeToggle from "./components/ThemeToggle";
import { US_ONLY_ERROR_MESSAGE } from "./utils/validateUsCity";

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
  const [fromCity, setFromCity] = useState("");
  const [toCity, setToCity] = useState("");
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

  function clearSearchResults() {
    setCarriers([]);
    setRoutes([]);
    setCarrierStatus("idle");
  }

  async function handleSearch(searchPayload = {}) {
    const resolvedFrom = searchPayload.fromCity ?? fromCity;
    const resolvedTo = searchPayload.toCity ?? toCity;

    setLoading(true);
    setError("");
    clearSearchResults();

    try {
      const result = await searchRoutes(resolvedFrom, resolvedTo);
      setCarriers(result.carriers);
      setRoutes(result.routes);
      setCarrierStatus(result.carriers.length ? "results" : "empty");
    } catch (searchError) {
      clearSearchResults();
      if (
        searchError instanceof SearchRequestError &&
        searchError.status === 422
      ) {
        setError(US_ONLY_ERROR_MESSAGE);
      } else {
        setError(
          searchError.message ||
            "Unable to complete the search. Check that the backend is running."
        );
      }
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
        onFromChange={(value) => {
          setFromCity(value);
          setError("");
        }}
        onToChange={(value) => {
          setToCity(value);
          setError("");
        }}
        onSearch={handleSearch}
        onValidationError={(message) => {
          setError(message);
          if (message) {
            clearSearchResults();
          }
        }}
        loading={loading}
      />
      {error ? (
        <p className="error-banner" role="alert">
          {error}
        </p>
      ) : null}
      <RouteMaps routes={routes} />
      <CarrierList carriers={carriers} status={carrierStatus} />
    </main>
  );
}
