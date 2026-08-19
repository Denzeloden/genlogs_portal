import os
import re

import httpx

US_ONLY_ERROR_MESSAGE = (
    "Unable to complete the search. Please choose a location within the US"
)

US_STATE_CODES = frozenset(
    {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    }
)

STATE_SUFFIX_PATTERN = re.compile(r"(?:,\s*|\s+)([A-Z]{2})\s*$", re.IGNORECASE)

NON_US_COUNTRY_SUFFIX = re.compile(
    r",\s*(?:"
    r"France|United Kingdom|UK|England|Scotland|Wales|Northern Ireland|"
    r"Canada|Mexico|Germany|Italy|Spain|Japan|China|Australia|Brazil|India|"
    r"Ireland|Netherlands|Belgium|Switzerland|Austria|Portugal|Sweden|Norway|"
    r"Denmark|Finland|Poland|Greece|Turkey|Russia|South Korea|Argentina|"
    r"Chile|Colombia|Peru|Venezuela|Egypt|South Africa|Nigeria|Kenya|Israel|"
    r"United Arab Emirates|UAE|Saudi Arabia|Singapore|Hong Kong|Taiwan|New Zealand"
    r")\s*$",
    re.IGNORECASE,
)

FOREIGN_CITY_NAMES = frozenset(
    {
        "london",
        "paris",
        "toronto",
        "vancouver",
        "montreal",
        "berlin",
        "madrid",
        "rome",
        "tokyo",
        "beijing",
        "shanghai",
        "sydney",
        "melbourne",
        "mumbai",
        "delhi",
        "dubai",
        "amsterdam",
        "brussels",
        "zurich",
        "vienna",
        "stockholm",
        "oslo",
        "copenhagen",
        "helsinki",
        "warsaw",
        "athens",
        "istanbul",
        "moscow",
        "seoul",
        "singapore",
        "hong kong",
        "auckland",
        "mexico city",
        "buenos aires",
        "sao paulo",
        "rio de janeiro",
        "cairo",
        "lagos",
        "nairobi",
        "tel aviv",
        "jerusalem",
        "medellin",
        "medellín",
        "lima",
        "caracas",
        "havana",
        "dublin",
        "munich",
        "frankfurt",
        "prague",
        "budapest",
        "lisbon",
        "casablanca",
        "bangkok",
        "manila",
        "jakarta",
        "taipei",
        "osaka",
        "kyoto",
        "nagoya",
        "kuala lumpur",
        "ho chi minh city",
        "hanoi",
        "bengaluru",
        "bangalore",
        "kolkata",
        "chennai",
        "karachi",
        "islamabad",
        "riyadh",
        "doha",
        "accra",
        "addis ababa",
        "cape town",
        "johannesburg",
    }
)


def _passes_heuristic(city: str) -> bool:
    cleaned = city.strip()
    if not cleaned:
        return False

    if NON_US_COUNTRY_SUFFIX.search(cleaned):
        return False

    state_match = STATE_SUFFIX_PATTERN.search(cleaned)
    if state_match:
        return state_match.group(1).upper() in US_STATE_CODES

    if "," in cleaned:
        return False

    return cleaned.lower() not in FOREIGN_CITY_NAMES


def _format_geocode_city(result: dict) -> str:
    components = result.get("address_components") or []
    city = next(
        (
            component["long_name"]
            for component in components
            if "locality" in component.get("types", [])
        ),
        None,
    )
    state = next(
        (
            component["short_name"]
            for component in components
            if "administrative_area_level_1" in component.get("types", [])
        ),
        None,
    )

    if city and state:
        return f"{city}, {state}"

    return result.get("formatted_address", "")


def _geocode_us_city(city: str) -> tuple[bool | None, str | None]:
    api_key = os.getenv("GOOGLE_MAPS_EMBED_KEY")
    if not api_key:
        return None, None

    try:
        response = httpx.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": city,
                "components": "country:US",
                "key": api_key,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        if status == "ZERO_RESULTS":
            return False, None
        if status != "OK" or not data.get("results"):
            return None, None

        result = data["results"][0]
        for component in result.get("address_components") or []:
            if "country" in component.get("types", []):
                if component.get("short_name") != "US":
                    return False, None
                break
        else:
            return False, None

        normalized_city = _format_geocode_city(result) or city.strip()
        return True, normalized_city
    except httpx.HTTPError:
        return None, None


def is_us_city(city: str) -> bool:
    cleaned = city.strip()
    if not _passes_heuristic(cleaned):
        return False

    is_us, _normalized_city = _geocode_us_city(cleaned)
    if is_us is False:
        return False
    if is_us is True:
        return True

    return True


def normalize_us_city(city: str) -> str:
    cleaned = city.strip()
    if not cleaned:
        return cleaned

    is_us, normalized_city = _geocode_us_city(cleaned)
    if is_us and normalized_city:
        return normalized_city

    return cleaned
