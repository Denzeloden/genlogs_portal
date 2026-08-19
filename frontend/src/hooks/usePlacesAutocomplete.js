import { useEffect, useRef } from "react";
import { formatPlaceCity } from "../utils/validateUsCity";

export const US_CITY_AUTOCOMPLETE_OPTIONS = {
  componentRestrictions: { country: "us" },
  types: ["(cities)"],
};

let mapsScriptPromise = null;

export function loadGoogleMapsPlaces(apiKey) {
  if (!apiKey) {
    return Promise.reject(new Error("Google Maps API key is not configured."));
  }

  if (window.google?.maps?.places) {
    return Promise.resolve();
  }

  if (!mapsScriptPromise) {
    mapsScriptPromise = new Promise((resolve, reject) => {
      const existing = document.querySelector('script[data-google-maps="places"]');
      if (existing) {
        existing.addEventListener("load", () => resolve(), { once: true });
        existing.addEventListener("error", () => reject(new Error("Failed to load Google Maps.")), {
          once: true,
        });
        return;
      }

      const script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
      script.async = true;
      script.defer = true;
      script.dataset.googleMaps = "places";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Google Maps."));
      document.head.appendChild(script);
    });
  }

  return mapsScriptPromise;
}

function isUnitedStatesPlace(place) {
  const country = place?.address_components?.find((component) =>
    component.types.includes("country")
  );
  return country?.short_name === "US";
}

export function usePlacesAutocomplete(inputRef, onPlaceSelected, enabled = true) {
  const autocompleteRef = useRef(null);
  const onPlaceSelectedRef = useRef(onPlaceSelected);

  useEffect(() => {
    onPlaceSelectedRef.current = onPlaceSelected;
  }, [onPlaceSelected]);

  useEffect(() => {
    if (!enabled || !inputRef.current) {
      return undefined;
    }

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    if (!apiKey) {
      return undefined;
    }

    let cancelled = false;

    loadGoogleMapsPlaces(apiKey)
      .then(() => {
        if (cancelled || !inputRef.current) {
          return;
        }

        autocompleteRef.current = new window.google.maps.places.Autocomplete(
          inputRef.current,
          US_CITY_AUTOCOMPLETE_OPTIONS
        );

        autocompleteRef.current.addListener("place_changed", () => {
          const place = autocompleteRef.current.getPlace();
          if (!place?.place_id || !isUnitedStatesPlace(place)) {
            return;
          }

          const label = formatPlaceCity(place);
          if (!label) {
            return;
          }

          onPlaceSelectedRef.current({
            label,
            placeId: place.place_id,
          });
        });
      })
      .catch((error) => {
        console.warn(error.message);
      });

    return () => {
      cancelled = true;
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(autocompleteRef.current);
        autocompleteRef.current = null;
      }
    };
  }, [enabled, inputRef]);
}
