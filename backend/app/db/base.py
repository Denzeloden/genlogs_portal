import os

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://genlogs:genlogs@localhost:5432/genlogs",
    )
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://") and not database_url.startswith(
        "postgresql+"
    ):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url
