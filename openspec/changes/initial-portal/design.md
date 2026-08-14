# Initial Portal — Design

## Stack
- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy 2.x + Alembic
- Database: PostgreSQL 16 (Docker local, Heroku Postgres prod)
- Maps: Google Maps iframe embed
- Deploy: Heroku (Node + Python buildpacks)

## Data Flow
1. User submits from/to cities via React
2. FastAPI queries sightings JOIN vehicles JOIN carriers
3. Aggregates COUNT(sightings) GROUP BY carrier
4. Falls back to wildcard lane (`*`, `*`) for default route
5. Returns carriers + 3 route embed URLs

## Schema
- carriers, vehicles, sightings (see database spec)
