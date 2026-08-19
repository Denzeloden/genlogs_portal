import { useRef } from "react";
import { usePlacesAutocomplete } from "../hooks/usePlacesAutocomplete";

const hasPlacesAutocomplete = Boolean(import.meta.env.VITE_GOOGLE_MAPS_API_KEY);

export default function SearchForm({
  fromCity,
  toCity,
  onFromChange,
  onToChange,
  onSearch,
  loading,
}) {
  const fromInputRef = useRef(null);
  const toInputRef = useRef(null);

  usePlacesAutocomplete(fromInputRef, onFromChange, hasPlacesAutocomplete);
  usePlacesAutocomplete(toInputRef, onToChange, hasPlacesAutocomplete);

  return (
    <section className="search-panel">
      <h1>GenLogs Carrier Route Search</h1>
      <p className="subtitle">
        Find top carriers moving between two US cities using simulated Trident sightings.
        {hasPlacesAutocomplete ? " City search is limited to the United States." : null}
      </p>
      <div className="search-form">
        <label>
          From (US city)
          <input
            ref={fromInputRef}
            type="text"
            value={fromCity}
            placeholder="New York City"
            autoComplete="off"
            onChange={(event) => onFromChange(event.target.value)}
          />
        </label>
        <label>
          To (US city)
          <input
            ref={toInputRef}
            type="text"
            value={toCity}
            placeholder="Washington DC"
            autoComplete="off"
            onChange={(event) => onToChange(event.target.value)}
          />
        </label>
        <button type="button" onClick={onSearch} disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
    </section>
  );
}
