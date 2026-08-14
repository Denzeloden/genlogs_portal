# Validation Test Matrix

Run these searches after starting the backend (seeded) and frontend.

| # | From | To | Expected Carriers | Expected Counts |
|---|------|----|-------------------|-----------------|
| 1 | New York City | Washington DC | Knight-Swift Transport Services | 10 Trucks/Day |
| 1 | | | J.B. Hunt Transport Services Inc | 7 Trucks/Day |
| 1 | | | YRC Worldwide | 5 Trucks/Day |
| 2 | San Francisco | Los Angeles | XPO Logistics | 9 Trucks/Day |
| 2 | | | Schneider | 6 Trucks/Day |
| 2 | | | Landstar Systems | 2 Trucks/Day |
| 3 | Chicago | Dallas | UPS Inc. | 11 Trucks/Day |
| 3 | | | FedEx Corp | 9 Trucks/Day |

## Additional Checks

- [ ] `GET /api/health` returns `{ "database": "ok", "sighting_count": > 0 }`
- [ ] `POST /api/search` returns exactly 3 route options with embed URLs
- [ ] Frontend renders 3 Google Maps iframes after search
- [ ] `/docs` shows FastAPI Swagger UI
- [ ] Production build serves React at `/` when `frontend/dist` exists

## Automated Tests

```powershell
cd backend
pytest tests/test_search.py -v
```

Tests cover all three route rules and health check using an in-memory SQLite database.
