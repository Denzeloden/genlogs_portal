from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CarrierProfile, SightingRecord, VehicleProfile
from app.services.route_embed import (
    ROUTE_A_FROM,
    ROUTE_A_TO,
    ROUTE_B_FROM,
    ROUTE_B_TO,
    WILDCARD_DEST,
    WILDCARD_ORIGIN,
    normalize_city,
    normalize_city_key,
)


def _is_route_a(from_key: str, to_key: str) -> bool:
    return from_key == ROUTE_A_FROM and to_key == ROUTE_A_TO


def _is_route_b(from_key: str, to_key: str) -> bool:
    return from_key == ROUTE_B_FROM and to_key == ROUTE_B_TO


def _query_carriers(
    db: Session, from_city: str, to_city: str
) -> list[tuple[str, int]]:
    statement = (
        select(CarrierProfile.name, func.count(SightingRecord.id))
        .join(VehicleProfile, VehicleProfile.carrier_id == CarrierProfile.id)
        .join(SightingRecord, SightingRecord.vehicle_id == VehicleProfile.id)
        .where(
            func.lower(SightingRecord.origin_city_inferred) == from_city.lower(),
            func.lower(SightingRecord.dest_city_inferred) == to_city.lower(),
        )
        .group_by(CarrierProfile.id, CarrierProfile.name)
        .order_by(func.count(SightingRecord.id).desc())
    )
    return [(name, int(count)) for name, count in db.execute(statement).all()]


def search_carriers(db: Session, from_city: str, to_city: str) -> list[dict]:
    normalized_from = normalize_city(from_city)
    normalized_to = normalize_city(to_city)
    from_key = normalize_city_key(normalized_from)
    to_key = normalize_city_key(normalized_to)

    results = _query_carriers(db, normalized_from, normalized_to)

    if not results and not _is_route_a(from_key, to_key) and not _is_route_b(
        from_key, to_key
    ):
        results = _query_carriers(db, WILDCARD_ORIGIN, WILDCARD_DEST)

    return [
        {"name": name, "trucks_per_day": count}
        for name, count in results
    ]
