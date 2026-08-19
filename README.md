# GenLogs Portal

Prototype web portal simulating the GenLogs platform: search origin/destination cities, view the top 3 fastest routes on Google Maps, and see carriers ranked by daily truck volume from PostgreSQL-seeded mock sightings.

## Stack

- **Frontend:** React + Vite
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Database:** PostgreSQL 16
- **Deploy:** Heroku (Node + Python buildpacks, Postgres addon)

## Quick Start (Local)

### Prerequisites

- Docker Desktop (for PostgreSQL)
- Node.js 20+
- Python 3.12+

### 1. Start PostgreSQL

```powershell
docker compose up -d db
```

### 2. Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_mock_data.py
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `/docs`.

### 3. Frontend setup (separate terminal)

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` with API proxy to backend.

### 4. Production-style local test

```powershell
cd frontend
npm run build
cd ..\backend
uvicorn app.main:app --reload
```

Visit `http://localhost:8000` — FastAPI serves the compiled React app.

## Demo City Pairs

| From | To | Expected Carriers |
|------|----|-------------------|
| New York City | Washington DC | Knight-Swift (10), J.B. Hunt (7), YRC (5) |
| San Francisco | Los Angeles | XPO (9), Schneider (6), Landstar (2) |
| Chicago | Dallas | UPS (11), FedEx (9) |
| Seattle | Boston | UPS (11), FedEx (9) — Route C default |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes (prod) | PostgreSQL connection string |
| `GOOGLE_MAPS_EMBED_KEY` | No | Google Maps Embed API key for route iframes |
| `VITE_GOOGLE_MAPS_API_KEY` | No | Google Maps JavaScript API key for US city autocomplete |

Local default: `postgresql://genlogs:genlogs@localhost:5432/genlogs`

## Tests

```powershell
cd backend
pip install -r requirements.txt
pytest
```

## Heroku Deployment

1. Create Heroku app and add Postgres addon
2. Set buildpacks: Node.js first, then Python
3. Push to Heroku — release phase runs migrations + seed
4. Optional: set `GOOGLE_MAPS_EMBED_KEY` config var

```powershell
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0
heroku buildpacks:add --index 1 heroku/nodejs
heroku buildpacks:add --index 2 heroku/python
git push heroku main
```

## Project Structure

```
genlogs-portal/
├── backend/          # FastAPI app, models, migrations, seed script
├── frontend/         # React SPA
├── openspec/         # Open Spec SDD artifacts
├── docs/             # Architecture, database design, reference docs
├── docker-compose.yml
├── Procfile
└── README.md
```

## Documentation

- [Architecture](docs/architecture.md)
- [Database Design](docs/database-design.md)
- [Validation Test Matrix](docs/validation-test-matrix.md)
- [Reference Docs](docs/reference/)
- [Development Prompts](docs/prompts/development-prompts.md)

## License

MIT
