import re

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
    }
)


def is_us_city(city: str) -> bool:
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
