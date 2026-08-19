import os
import re
from urllib.parse import quote_plus

ROUTE_A_FROM = "new york city"
ROUTE_A_TO = "washington dc"
ROUTE_B_FROM = "san francisco"
ROUTE_B_TO = "los angeles"
WILDCARD_ORIGIN = "*"
WILDCARD_DEST = "*"

STATE_SUFFIX = re.compile(r",\s*[A-Z]{2}$", re.IGNORECASE)

LANE_CITY_ALIASES = {
    "new york": "New York City",
    "new york city": "New York City",
    "washington": "Washington DC",
    "washington dc": "Washington DC",
    "san francisco": "San Francisco",
    "los angeles": "Los Angeles",
}

ROUTE_LABELS = ("Fastest", "Avoid Tolls", "Avoid Highways")

ROUTE_METADATA = {
    (ROUTE_A_FROM, ROUTE_A_TO): [
        ("3h 45m", "225 mi"),
        ("4h 10m", "240 mi"),
        ("4h 30m", "255 mi"),
    ],
    (ROUTE_B_FROM, ROUTE_B_TO): [
        ("5h 30m", "380 mi"),
        ("6h 00m", "400 mi"),
        ("6h 20m", "415 mi"),
    ],
}

DEFAULT_ROUTE_METADATA = [
    ("8h 00m", "500 mi"),
    ("8h 30m", "520 mi"),
    ("9h 00m", "540 mi"),
]

ROUTE_AVOID = {
    0: None,
    1: "tolls",
    2: "highways",
}

FALLBACK_DIRFLG = {
    0: "",
    1: "t",
    2: "h",
}


def normalize_city(city: str) -> str:
    cleaned = STATE_SUFFIX.sub("", city.strip()).strip()
    return LANE_CITY_ALIASES.get(cleaned.lower(), cleaned)


def normalize_city_key(city: str) -> str:
    return normalize_city(city).lower()


def build_embed_url(from_city: str, to_city: str, route_index: int) -> str:
    api_key = os.getenv("GOOGLE_MAPS_EMBED_KEY")
    origin = quote_plus(from_city)
    destination = quote_plus(to_city)
    avoid = ROUTE_AVOID.get(route_index)

    if api_key:
        url = (
            f"https://www.google.com/maps/embed/v1/directions"
            f"?key={api_key}&origin={origin}&destination={destination}&mode=driving"
        )
        if avoid:
            url += f"&avoid={avoid}"
        return url

    dirflg = FALLBACK_DIRFLG.get(route_index, "")
    url = (
        f"https://maps.google.com/maps?saddr={origin}&daddr={destination}"
        f"&output=embed&hl=en"
    )
    if dirflg:
        url += f"&dirflg={dirflg}"
    return url


def get_route_options(from_city: str, to_city: str) -> list[dict]:
    from_key = normalize_city_key(from_city)
    to_key = normalize_city_key(to_city)
    metadata = ROUTE_METADATA.get((from_key, to_key), DEFAULT_ROUTE_METADATA)

    routes = []
    for index, label in enumerate(ROUTE_LABELS):
        duration_text, distance_text = metadata[index]
        routes.append(
            {
                "label": label,
                "duration_text": duration_text,
                "distance_text": distance_text,
                "embed_url": build_embed_url(from_city, to_city, index),
            }
        )
    return routes
