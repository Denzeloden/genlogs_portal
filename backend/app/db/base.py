import os

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://genlogs:genlogs@localhost:5432/genlogs",
    )
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return database_url
