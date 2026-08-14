import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CarrierProfile(Base):
    __tablename__ = "carriers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dot_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mc_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_fmcsa_sync: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    vehicles: Mapped[list["VehicleProfile"]] = relationship(
        back_populates="carrier", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("carriers_dot_number_idx", "dot_number"),)


class VehicleProfile(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    carrier_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("carriers.id"), nullable=False
    )
    vin: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    license_plate: Mapped[str | None] = mapped_column(String(20), nullable=True)
    plate_state: Mapped[str | None] = mapped_column(String(2), nullable=True)

    carrier: Mapped["CarrierProfile"] = relationship(back_populates="vehicles")
    sightings: Mapped[list["SightingRecord"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )


class SightingRecord(Base):
    __tablename__ = "sightings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("vehicles.id"), nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    origin_city_inferred: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dest_city_inferred: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    vehicle: Mapped["VehicleProfile"] = relationship(back_populates="sightings")

    __table_args__ = (
        Index("sightings_origin_city_inferred_idx", "origin_city_inferred"),
        Index("sightings_dest_city_inferred_idx", "dest_city_inferred"),
    )
