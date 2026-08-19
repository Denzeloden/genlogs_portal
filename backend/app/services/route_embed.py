import os
import re
from urllib.parse import quote_plus

import httpx

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

ROUTE_LABELS = ("Fastest Route 1", "Fastest Route 2", "Fastest Route 3")
ROUTE_COUNT = 3

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

ROUTE_WAYPOINTS = {
    (ROUTE_A_FROM, ROUTE_A_TO): [None, "Philadelphia, PA", "Wilmington, DE"],
    (ROUTE_B_FROM, ROUTE_B_TO): [None, "San Jose, CA", "Santa Barbara, CA"],
}

WAYPOINT_FRACTIONS = (0.35, 0.65)


def normalize_city(city: str) -> str:
    cleaned = STATE_SUFFIX.sub("", city.strip()).strip()
    return LANE_CITY_ALIASES.get(cleaned.lower(), cleaned)


def normalize_city_key(city: str) -> str:
    return normalize_city(city).lower()


def _route_duration_seconds(route: dict) -> int:
    total = 0
    for leg in route.get("legs") or []:
        total += leg.get("duration", {}).get("value", 0)
    return total


def _route_distance_meters(route: dict) -> int:
    total = 0
    for leg in route.get("legs") or []:
        total += leg.get("distance", {}).get("value", 0)
    return total


def _format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}m"


def _format_distance(meters: int) -> str:
    miles = round(meters / 1609.34)
    return f"{miles} mi"


def _route_point(
    city: str,
    lat: float | None = None,
    lng: float | None = None,
) -> str:
    if lat is not None and lng is not None:
        return f"{lat},{lng}"
    return city


def _fetch_fastest_routes(origin: str, destination: str) -> list[dict]:
    api_key = os.getenv("GOOGLE_MAPS_EMBED_KEY")
    if not api_key:
        return []

    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "alternatives": "true",
        "key": api_key,
    }

    try:
        response = httpx.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params=params,
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "OK" or not data.get("routes"):
            return []

        return sorted(data["routes"], key=_route_duration_seconds)[:ROUTE_COUNT]
    except httpx.HTTPError:
        return []


def _waypoint_from_route(route: dict, fraction: float) -> str | None:
    steps = []
    for leg in route.get("legs") or []:
        steps.extend(leg.get("steps") or [])

    if len(steps) < 2:
        return None

    index = min(int(len(steps) * fraction), len(steps) - 1)
    location = steps[index].get("end_location") or {}
    lat = location.get("lat")
    lng = location.get("lng")
    if lat is None or lng is None:
        return None
    return f"{lat},{lng}"


def _waypoint_for_route(route: dict) -> str | None:
    return _waypoint_from_route(route, 0.5)


def build_embed_url(
    origin: str,
    destination: str,
    waypoint: str | None = None,
) -> str:
    api_key = os.getenv("GOOGLE_MAPS_EMBED_KEY")
    origin = quote_plus(origin)
    destination = quote_plus(destination)

    if api_key:
        url = (
            f"https://www.google.com/maps/embed/v1/directions"
            f"?key={api_key}&origin={origin}&destination={destination}&mode=driving"
        )
        if waypoint:
            url += f"&waypoints={quote_plus(waypoint)}"
        return url

    daddr = destination
    if waypoint:
        daddr = f"{quote_plus(waypoint)}+to:{destination}"

    return (
        f"https://maps.google.com/maps?saddr={origin}&daddr={daddr}"
        f"&output=embed&hl=en"
    )


def get_route_options(
    from_city: str,
    to_city: str,
    from_lat: float | None = None,
    from_lng: float | None = None,
    to_lat: float | None = None,
    to_lng: float | None = None,
) -> list[dict]:
    from_key = normalize_city_key(from_city)
    to_key = normalize_city_key(to_city)
    origin = _route_point(from_city, from_lat, from_lng)
    destination = _route_point(to_city, to_lat, to_lng)
    mock_metadata = ROUTE_METADATA.get((from_key, to_key), DEFAULT_ROUTE_METADATA)
    fallback_waypoints = ROUTE_WAYPOINTS.get((from_key, to_key), [None, None, None])
    fastest_routes = _fetch_fastest_routes(origin, destination)

    routes = []
    for index in range(ROUTE_COUNT):
        if index < len(fastest_routes):
            route = fastest_routes[index]
            duration_text = _format_duration(_route_duration_seconds(route))
            distance_text = _format_distance(_route_distance_meters(route))
            waypoint = None if index == 0 else _waypoint_for_route(route)
        else:
            duration_text, distance_text = mock_metadata[index]
            waypoint = fallback_waypoints[index]
            if waypoint is None and fastest_routes and index > 0:
                fraction = WAYPOINT_FRACTIONS[index - 1]
                waypoint = _waypoint_from_route(fastest_routes[0], fraction)

        if waypoint is None and index > 0:
            waypoint = fallback_waypoints[index]

        routes.append(
            {
                "label": ROUTE_LABELS[index],
                "duration_text": duration_text,
                "distance_text": distance_text,
                "embed_url": build_embed_url(origin, destination, waypoint),
            }
        )

    return routes
