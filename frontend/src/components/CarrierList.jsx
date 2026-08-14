export default function CarrierList({ carriers }) {
  if (!carriers.length) {
    return (
      <section className="carriers-panel">
        <h2>Carriers</h2>
        <p className="empty-state">Run a search to see carrier volume for this lane.</p>
      </section>
    );
  }

  return (
    <section className="carriers-panel">
      <h2>Carriers</h2>
      <ul className="carrier-list">
        {carriers.map((carrier) => (
          <li key={carrier.name}>
            <strong>{carrier.name}</strong>
            <span>{carrier.trucks_per_day} Trucks/Day</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
