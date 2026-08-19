import { loadGoogleMapsPlaces } from "../hooks/usePlacesAutocomplete";

export const US_ONLY_ERROR_MESSAGE =
  "Unable to complete the search. Please choose a location within the US";

export const DROPDOWN_REQUIRED_MESSAGE =
  "Please select a location from the dropdown";

const US_GEOCODE_OPTIONS = {
  componentRestrictions: { country: "us" },
};

const US_STATE_CODES = new Set([
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID",
  "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
  "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
  "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]);

const NON_US_COUNTRY_SUFFIX =
  /,\s*(?:France|United Kingdom|UK|England|Scotland|Wales|Northern Ireland|Canada|Mexico|Germany|Italy|Spain|Japan|China|Australia|Brazil|India|Ireland|Netherlands|Belgium|Switzerland|Austria|Portugal|Sweden|Norway|Denmark|Finland|Poland|Greece|Turkey|Russia|South Korea|Argentina|Chile|Colombia|Peru|Venezuela|Egypt|South Africa|Nigeria|Kenya|Israel|United Arab Emirates|UAE|Saudi Arabia|Singapore|Hong Kong|Taiwan|New Zealand)\s*$/i;

const STATE_SUFFIX_PATTERN = /(?:,\s*|\s+)([A-Z]{2})\s*$/i;

const FOREIGN_CITY_NAMES = new Set([
  "london", "paris", "toronto", "vancouver", "montreal", "berlin", "madrid", "rome",
  "tokyo", "beijing", "shanghai", "sydney", "melbourne", "mumbai", "delhi", "dubai",
  "amsterdam", "brussels", "zurich", "vienna", "stockholm", "oslo", "copenhagen",
  "helsinki", "warsaw", "athens", "istanbul", "moscow", "seoul", "singapore",
  "hong kong", "auckland", "mexico city", "buenos aires", "sao paulo",
  "rio de janeiro", "cairo", "lagos", "nairobi", "tel aviv", "jerusalem",
  "medellin", "medellín", "lima", "caracas", "havana", "dublin", "munich",
  "frankfurt", "prague", "budapest", "lisbon", "casablanca", "bangkok", "manila",
  "jakarta", "taipei", "osaka", "kyoto", "kuala lumpur", "ho chi minh city", "hanoi",
  "bengaluru", "bangalore", "kolkata", "chennai", "karachi", "islamabad", "riyadh",
  "doha", "accra", "addis ababa", "cape town", "johannesburg",
]);

export function formatPlaceCity(place) {
  if (!place?.address_components?.length) {
    return place?.name || place?.formatted_address || "";
  }

  const city = place.address_components.find((component) =>
    component.types.includes("locality")
  );
  const state = place.address_components.find((component) =>
    component.types.includes("administrative_area_level_1")
  );

  if (city && state) {
    return `${city.long_name}, ${state.short_name}`;
  }

  return place.name || place.formatted_address || "";
}

function formatGeocodeCity(result) {
  const components = result.address_components || [];
  const city = components.find((component) => component.types.includes("locality"));
  const state = components.find((component) =>
    component.types.includes("administrative_area_level_1")
  );

  if (city && state) {
    return `${city.long_name}, ${state.short_name}`;
  }

  return result.formatted_address || "";
}

export function isUsCityHeuristic(city) {
  const cleaned = city.trim();
  if (!cleaned) {
    return false;
  }

  if (NON_US_COUNTRY_SUFFIX.test(cleaned)) {
    return false;
  }

  const stateMatch = cleaned.match(STATE_SUFFIX_PATTERN);
  if (stateMatch) {
    return US_STATE_CODES.has(stateMatch[1].toUpperCase());
  }

  if (cleaned.includes(",")) {
    return false;
  }

  return !FOREIGN_CITY_NAMES.has(cleaned.toLowerCase());
}

function geocodeUsCity(city) {
  return new Promise((resolve) => {
    const geocoder = new window.google.maps.Geocoder();
    geocoder.geocode(
      { address: city, ...US_GEOCODE_OPTIONS },
      (results, status) => {
        if (status !== "OK" || !results?.length) {
          resolve({ valid: false, normalizedCity: null });
          return;
        }

        const result = results[0];
        const country = result.address_components?.find((component) =>
          component.types.includes("country")
        );

        if (country?.short_name !== "US") {
          resolve({ valid: false, normalizedCity: null });
          return;
        }

        resolve({
          valid: true,
          normalizedCity: formatGeocodeCity(result) || city.trim(),
        });
      }
    );
  });
}

export async function resolveUsCity(city) {
  const cleaned = city.trim();
  if (!cleaned || !isUsCityHeuristic(cleaned)) {
    return { valid: false, normalizedCity: null };
  }

  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  if (!apiKey) {
    return { valid: true, normalizedCity: cleaned };
  }

  try {
    await loadGoogleMapsPlaces(apiKey);
    return geocodeUsCity(cleaned);
  } catch {
    return {
      valid: isUsCityHeuristic(cleaned),
      normalizedCity: cleaned,
    };
  }
}

export async function validateUsCity(city) {
  const result = await resolveUsCity(city);
  return result.valid;
}
