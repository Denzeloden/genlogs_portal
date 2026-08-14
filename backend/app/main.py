import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select, text

from app.db.session import SessionLocal, engine
from app.models import SightingRecord
from app.routers.search import router as search_router

logger = logging.getLogger(__name__)

app = FastAPI(title="GenLogs Portal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)


@app.get("/api/health")
def health_check() -> dict:
    db_status = "ok"
    sighting_count = 0
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            sighting_count = db.scalar(select(func.count(SightingRecord.id))) or 0
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "sighting_count": sighting_count,
    }


@app.on_event("startup")
def startup_event() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        with SessionLocal() as db:
            count = db.scalar(select(func.count(SightingRecord.id))) or 0
            if count == 0:
                logger.warning(
                    "Database is empty. Run: alembic upgrade head && "
                    "python scripts/seed_mock_data.py"
                )
    except Exception as exc:
        logger.warning("Database connection failed on startup: %s", exc)


frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str) -> FileResponse:
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
