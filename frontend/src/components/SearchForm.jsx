export default function SearchForm({ fromCity, toCity, onFromChange, onToChange, onSearch, loading }) {
  return (
    <section className="search-panel">
      <h1>GenLogs Carrier Route Search</h1>
      <p className="subtitle">
        Find top carriers moving between two cities using simulated Trident sightings.
      </p>
      <div className="search-form">
        <label>
          From (city)
          <input
            type="text"
            value={fromCity}
            placeholder="New York City"
            onChange={(event) => onFromChange(event.target.value)}
          />
        </label>
        <label>
          To (city)
          <input
            type="text"
            value={toCity}
            placeholder="Washington DC"
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
