release: cd backend && alembic upgrade head && python scripts/seed_mock_data.py
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
