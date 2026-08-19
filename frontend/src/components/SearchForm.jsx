import { useRef, useState } from "react";
import { usePlacesAutocomplete } from "../hooks/usePlacesAutocomplete";
import {
  DROPDOWN_REQUIRED_MESSAGE,
  resolveUsCity,
  US_ONLY_ERROR_MESSAGE,
} from "../utils/validateUsCity";

const hasPlacesAutocomplete = Boolean(import.meta.env.VITE_GOOGLE_MAPS_API_KEY);

export default function SearchForm({
  fromCity,
  toCity,
  onFromChange,
  onToChange,
  onSearch,
  onValidationError,
  loading,
}) {
  const fromInputRef = useRef(null);
  const toInputRef = useRef(null);
  const [fromPlaceId, setFromPlaceId] = useState(null);
  const [toPlaceId, setToPlaceId] = useState(null);
  const [fromCoords, setFromCoords] = useState(null);
  const [toCoords, setToCoords] = useState(null);

  usePlacesAutocomplete(
    fromInputRef,
    ({ label, placeId, lat, lng }) => {
      onFromChange(label);
      setFromPlaceId(placeId);
      setFromCoords({ lat, lng });
    },
    hasPlacesAutocomplete
  );

  usePlacesAutocomplete(
    toInputRef,
    ({ label, placeId, lat, lng }) => {
      onToChange(label);
      setToPlaceId(placeId);
      setToCoords({ lat, lng });
    },
    hasPlacesAutocomplete
  );

  function handleFromInputChange(value) {
    onFromChange(value);
    setFromPlaceId(null);
    setFromCoords(null);
  }

  function handleToInputChange(value) {
    onToChange(value);
    setToPlaceId(null);
    setToCoords(null);
  }

  const canSearch = hasPlacesAutocomplete
    ? Boolean(fromPlaceId && toPlaceId)
    : Boolean(fromCity.trim() && toCity.trim());

  async function handleSubmit() {
    try {
      if (hasPlacesAutocomplete) {
        if (!fromPlaceId || !toPlaceId) {
          onValidationError(DROPDOWN_REQUIRED_MESSAGE);
          return;
        }

        onValidationError("");
        await onSearch({
          fromCity,
          toCity,
          fromLat: fromCoords.lat,
          fromLng: fromCoords.lng,
          toLat: toCoords.lat,
          toLng: toCoords.lng,
        });
        return;
      }

      const [fromResult, toResult] = await Promise.all([
        resolveUsCity(fromCity),
        resolveUsCity(toCity),
      ]);

      if (!fromResult.valid || !toResult.valid) {
        onValidationError(US_ONLY_ERROR_MESSAGE);
        return;
      }

      onValidationError("");
      onFromChange(fromResult.normalizedCity);
      onToChange(toResult.normalizedCity);
      await onSearch({
        fromCity: fromResult.normalizedCity,
        toCity: toResult.normalizedCity,
      });
    } catch {
      onValidationError(US_ONLY_ERROR_MESSAGE);
    }
  }

  return (
    <section className="search-panel">
      <h1>GenLogs Carrier Route Search</h1>
      <p className="subtitle">
        Find top carriers moving between two US cities using simulated Trident sightings.
        {hasPlacesAutocomplete
          ? " Select both cities from the dropdown suggestions."
          : " City search is limited to the United States."}
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
            onChange={(event) => handleFromInputChange(event.target.value)}
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
            onChange={(event) => handleToInputChange(event.target.value)}
          />
        </label>
        <button
          type="button"
          className={!canSearch && !loading ? "search-button-awaiting" : undefined}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
    </section>
  );
}
