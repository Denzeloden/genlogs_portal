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
    throw new Error("Search request failed");
  }

  return response.json();
}
