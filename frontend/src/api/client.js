import { US_ONLY_ERROR_MESSAGE } from "../utils/validateUsCity";

export class SearchRequestError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "SearchRequestError";
    this.status = status;
  }
}

export async function searchRoutes({
  fromCity,
  toCity,
  fromLat,
  fromLng,
  toLat,
  toLng,
}) {
  const payload = {
    from_city: fromCity,
    to_city: toCity,
  };

  if (fromLat != null && fromLng != null) {
    payload.from_lat = fromLat;
    payload.from_lng = fromLng;
  }
  if (toLat != null && toLng != null) {
    payload.to_lat = toLat;
    payload.to_lng = toLng;
  }

  const response = await fetch("/api/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message =
      response.status === 422
        ? US_ONLY_ERROR_MESSAGE
        : typeof payload.detail === "string"
          ? payload.detail
          : "Search request failed";
    throw new SearchRequestError(message, response.status);
  }

  return response.json();
}
