export default function RouteMaps({ routes }) {
  if (!routes.length) {
    return null;
  }

  return (
    <section className="routes-panel">
      <h2>Top 3 Fastest Routes</h2>
      <div className="routes-grid">
        {routes.map((route, index) => (
          <article className="route-card" key={`${route.label}-${index}`}>
            <div className="route-meta">
              <h3>{route.label}</h3>
              <p>
                {route.duration_text} · {route.distance_text}
              </p>
            </div>
            <iframe
              title={`${route.label} route map`}
              src={route.embed_url}
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              allowFullScreen
            />
          </article>
        ))}
      </div>
    </section>
  );
}
