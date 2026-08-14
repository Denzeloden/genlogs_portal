"""Initial schema migration."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "carriers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dot_number", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("mc_number", sa.String(length=255), nullable=True),
        sa.Column("last_fmcsa_sync", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dot_number"),
    )
    op.create_index("carriers_dot_number_idx", "carriers", ["dot_number"])

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("carrier_id", sa.Uuid(), nullable=False),
        sa.Column("vin", sa.String(length=17), nullable=False),
        sa.Column("license_plate", sa.String(length=20), nullable=True),
        sa.Column("plate_state", sa.String(length=2), nullable=True),
        sa.ForeignKeyConstraint(["carrier_id"], ["carriers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vin"),
    )

    op.create_table(
        "sightings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vehicle_id", sa.Uuid(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("origin_city_inferred", sa.String(length=255), nullable=True),
        sa.Column("dest_city_inferred", sa.String(length=255), nullable=True),
        sa.Column("raw_image_url", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "sightings_origin_city_inferred_idx",
        "sightings",
        ["origin_city_inferred"],
    )
    op.create_index(
        "sightings_dest_city_inferred_idx",
        "sightings",
        ["dest_city_inferred"],
    )


def downgrade() -> None:
    op.drop_index("sightings_dest_city_inferred_idx", table_name="sightings")
    op.drop_index("sightings_origin_city_inferred_idx", table_name="sightings")
    op.drop_table("sightings")
    op.drop_table("vehicles")
    op.drop_index("carriers_dot_number_idx", table_name="carriers")
    op.drop_table("carriers")
