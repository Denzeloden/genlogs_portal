import { useState } from "react";
import { searchRoutes } from "./api/client";
import CarrierList from "./components/CarrierList";
import RouteMaps from "./components/RouteMaps";
import SearchForm from "./components/SearchForm";

export default function App() {
  const [fromCity, setFromCity] = useState("New York City");
  const [toCity, setToCity] = useState("Washington DC");
  const [carriers, setCarriers] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    setLoading(true);
    setError("");

    try {
      const result = await searchRoutes(fromCity, toCity);
      setCarriers(result.carriers);
      setRoutes(result.routes);
    } catch (searchError) {
      setCarriers([]);
      setRoutes([]);
      setError("Unable to complete the search. Check that the backend is running.");
      console.error(searchError);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
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
      <CarrierList carriers={carriers} />
    </main>
  );
}
