from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CarrierProfile, SightingRecord, VehicleProfile
from app.services.route_embed import normalize_city


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
    results = _query_carriers(db, normalized_from, normalized_to)

    return [
        {"name": name, "trucks_per_day": count}
        for name, count in results
    ]
