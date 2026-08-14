"""Seed mock SAFER-enriched carrier and sighting data."""

from __future__ import annotations

import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import func, select, delete

from app.db.session import SessionLocal
from app.models import CarrierProfile, SightingRecord, VehicleProfile

WILDCARD_ORIGIN = "*"
WILDCARD_DEST = "*"

LANE_SEED_DATA = [
    {
        "origin": "New York City",
        "dest": "Washington DC",
        "carriers": [
            {
                "dot_number": "520058",
                "name": "Knight-Swift Transport Services",
                "mc_number": "MC-135686",
                "trucks_per_day": 10,
                "license_plate": "TX-99827B",
                "plate_state": "TX",
            },
            {
                "dot_number": "80806",
                "name": "J.B. Hunt Transport Services Inc",
                "mc_number": "MC-135686",
                "trucks_per_day": 7,
                "license_plate": "AR-44102H",
                "plate_state": "AR",
            },
            {
                "dot_number": "261928",
                "name": "YRC Worldwide",
                "mc_number": "MC-132698",
                "trucks_per_day": 5,
                "license_plate": "KS-22001Y",
                "plate_state": "KS",
            },
        ],
    },
    {
        "origin": "San Francisco",
        "dest": "Los Angeles",
        "carriers": [
            {
                "dot_number": "241829",
                "name": "XPO Logistics",
                "mc_number": "MC-165714",
                "trucks_per_day": 9,
                "license_plate": "CA-81123X",
                "plate_state": "CA",
            },
            {
                "dot_number": "150331",
                "name": "Schneider",
                "mc_number": "MC-133655",
                "trucks_per_day": 6,
                "license_plate": "WI-55001S",
                "plate_state": "WI",
            },
            {
                "dot_number": "241572",
                "name": "Landstar Systems",
                "mc_number": "MC-166960",
                "trucks_per_day": 2,
                "license_plate": "FL-33002L",
                "plate_state": "FL",
            },
        ],
    },
    {
        "origin": WILDCARD_ORIGIN,
        "dest": WILDCARD_DEST,
        "carriers": [
            {
                "dot_number": "21800",
                "name": "UPS Inc.",
                "mc_number": "MC-139237",
                "trucks_per_day": 11,
                "license_plate": "NJ-77621P",
                "plate_state": "NJ",
            },
            {
                "dot_number": "86876",
                "name": "FedEx Corp",
                "mc_number": "MC-665332",
                "trucks_per_day": 9,
                "license_plate": "TN-99201F",
                "plate_state": "TN",
            },
        ],
    },
]

CAMERA_LOCATIONS = {
    ("New York City", "Washington DC"): (40.7128, -74.0060),
    ("San Francisco", "Los Angeles"): (37.7749, -122.4194),
    (WILDCARD_ORIGIN, WILDCARD_DEST): (41.8781, -87.6298),
}


def seed_mock_data(force: bool = False) -> None:
    captured_at = datetime(2024, 5, 12, 14, 22, tzinfo=UTC)

    with SessionLocal() as db:
        existing_carriers = db.scalar(select(func.count(CarrierProfile.id))) or 0
        if existing_carriers > 0 and not force:
            print("Seed skipped — data already exists.")
            return

        if existing_carriers > 0:
            db.execute(delete(SightingRecord))
            db.execute(delete(VehicleProfile))
            db.execute(delete(CarrierProfile))
            db.commit()

        for lane in LANE_SEED_DATA:
            origin = lane["origin"]
            dest = lane["dest"]
            latitude, longitude = CAMERA_LOCATIONS.get((origin, dest), (39.8283, -98.5795))

            for carrier_data in lane["carriers"]:
                carrier = CarrierProfile(
                    id=uuid.uuid4(),
                    dot_number=carrier_data["dot_number"],
                    name=carrier_data["name"],
                    mc_number=carrier_data["mc_number"],
                    last_fmcsa_sync=captured_at,
                )
                db.add(carrier)
                db.flush()

                vehicle = VehicleProfile(
                    id=uuid.uuid4(),
                    carrier_id=carrier.id,
                    vin=f"VIN{carrier_data['dot_number'][:8]}".ljust(17, "0")[:17],
                    license_plate=carrier_data["license_plate"],
                    plate_state=carrier_data["plate_state"],
                )
                db.add(vehicle)
                db.flush()

                for index in range(carrier_data["trucks_per_day"]):
                    sighting = SightingRecord(
                        id=uuid.uuid4(),
                        vehicle_id=vehicle.id,
                        captured_at=captured_at,
                        latitude=latitude,
                        longitude=longitude,
                        origin_city_inferred=origin,
                        dest_city_inferred=dest,
                        raw_image_url=(
                            f"https://storage.genlogs.mock/sightings/"
                            f"{carrier_data['dot_number']}-{index}.jpg"
                        ),
                    )
                    db.add(sighting)

        db.commit()


if __name__ == "__main__":
    seed_mock_data()
    print("Mock data seeded successfully.")
