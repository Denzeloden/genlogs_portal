export async function searchRoutes(fromCity, toCity) {
  const response = await fetch("/api/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from_city: fromCity,
      to_city: toCity,
    }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message =
      typeof payload.detail === "string"
        ? payload.detail
        : "Search request failed";
    throw new Error(message);
  }

  return response.json();
}
