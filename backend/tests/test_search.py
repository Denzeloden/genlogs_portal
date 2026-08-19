import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from scripts.seed_mock_data import seed_mock_data


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    import app.db.session as session_module
    import scripts.seed_mock_data as seed_module

    original_session_local = session_module.SessionLocal
    original_seed_session_local = seed_module.SessionLocal

    session_module.SessionLocal = TestingSessionLocal
    seed_module.SessionLocal = TestingSessionLocal

    seed_mock_data(force=True)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    session_module.SessionLocal = original_session_local
    seed_module.SessionLocal = original_seed_session_local


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["database"] == "ok"
    assert payload["sighting_count"] > 0


def test_route_a_carriers(client):
    response = client.post(
        "/api/search",
        json={"from_city": "New York City", "to_city": "Washington DC"},
    )
    assert response.status_code == 200
    carriers = response.json()["carriers"]
    assert len(carriers) == 3
    assert carriers[0] == {"name": "Knight-Swift Transport Services", "trucks_per_day": 10}
    assert carriers[1] == {"name": "J.B. Hunt Transport Services Inc", "trucks_per_day": 7}
    assert carriers[2] == {"name": "YRC Worldwide", "trucks_per_day": 5}


def test_route_b_carriers_with_state_suffixes(client):
    response = client.post(
        "/api/search",
        json={"from_city": "San Francisco, CA", "to_city": "Los Angeles, CA"},
    )
    assert response.status_code == 200
    carriers = response.json()["carriers"]
    assert len(carriers) == 3
    assert carriers[0] == {"name": "XPO Logistics", "trucks_per_day": 9}
    assert carriers[1] == {"name": "Schneider", "trucks_per_day": 6}
    assert carriers[2] == {"name": "Landstar Systems", "trucks_per_day": 2}


def test_route_a_carriers_with_state_suffixes(client):
    response = client.post(
        "/api/search",
        json={"from_city": "New York, NY", "to_city": "Washington, DC"},
    )
    assert response.status_code == 200
    carriers = response.json()["carriers"]
    assert len(carriers) == 3
    assert carriers[0]["name"] == "Knight-Swift Transport Services"


def test_route_b_carriers(client):
    response = client.post(
        "/api/search",
        json={"from_city": "San Francisco", "to_city": "Los Angeles"},
    )
    assert response.status_code == 200
    carriers = response.json()["carriers"]
    assert len(carriers) == 3
    assert carriers[0] == {"name": "XPO Logistics", "trucks_per_day": 9}
    assert carriers[1] == {"name": "Schneider", "trucks_per_day": 6}
    assert carriers[2] == {"name": "Landstar Systems", "trucks_per_day": 2}


def test_route_c_default_carriers(client):
    response = client.post(
        "/api/search",
        json={"from_city": "Seattle WA", "to_city": "Boston MA"},
    )
    assert response.status_code == 200
    carriers = response.json()["carriers"]
    assert len(carriers) == 2
    assert carriers[0] == {"name": "UPS Inc.", "trucks_per_day": 11}
    assert carriers[1] == {"name": "FedEx Corp", "trucks_per_day": 9}


def test_rejects_non_us_cities(client):
    response = client.post(
        "/api/search",
        json={"from_city": "London", "to_city": "Paris, France"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Unable to complete the search. Please choose a location within the US"
    )


def test_rejects_invalid_state_suffix(client):
    response = client.post(
        "/api/search",
        json={"from_city": "Toronto, ON", "to_city": "Boston, MA"},
    )
    assert response.status_code == 422


def test_search_returns_three_fastest_route_options(client):
    response = client.post(
        "/api/search",
        json={"from_city": "New York City", "to_city": "Washington DC"},
    )
    assert response.status_code == 200
    routes = response.json()["routes"]
    embed_urls = [route["embed_url"] for route in routes]
    assert len(routes) == 3
    assert routes[0]["label"] == "Fastest Route 1"
    assert routes[1]["label"] == "Fastest Route 2"
    assert routes[2]["label"] == "Fastest Route 3"
    assert len(set(embed_urls)) == 3
    assert "Philadelphia" in embed_urls[1]
    assert "Wilmington" in embed_urls[2]
    for embed_url in embed_urls:
        assert "avoid=" not in embed_url
        assert "dirflg=" not in embed_url


def test_search_uses_embed_api_without_avoid_filters(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_EMBED_KEY", "test-embed-key")
    response = client.post(
        "/api/search",
        json={"from_city": "New York City", "to_city": "Washington DC"},
    )
    assert response.status_code == 200
    routes = response.json()["routes"]
    for route in routes:
        assert "maps/embed/v1/directions" in route["embed_url"]
        assert "avoid=" not in route["embed_url"]
        assert "dirflg=" not in route["embed_url"]
    assert "waypoints=Philadelphia" in routes[1]["embed_url"]
    assert "waypoints=Wilmington" in routes[2]["embed_url"]
