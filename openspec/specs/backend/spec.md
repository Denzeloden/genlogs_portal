# GenLogs Portal — Backend Spec

## Requirements

### REQ-BE-001: Search Endpoint
The system SHALL expose `POST /api/search` accepting `{ from_city, to_city }` and returning carriers and route options.

### REQ-BE-002: Health Endpoint
The system SHALL expose `GET /api/health` verifying database connectivity.

### REQ-BE-003: Carrier Aggregation
The system SHALL query PostgreSQL sightings, join vehicles and carriers, and aggregate truck volume by carrier for the requested lane.

### REQ-BE-004: Route Fallback
When no exact lane match exists and cities are not Route A/B pairs, the system SHALL return wildcard lane carriers (UPS, FedEx).

### REQ-BE-005: Static Serving
In production, FastAPI SHALL serve the compiled React frontend as static files.
