# GenLogs Portal — Frontend Spec

## Requirements

### REQ-FE-001: Search Form
The system SHALL render a single-page application with "From (city)" and "To (city)" input fields and a "Search" button.

### REQ-FE-002: Route Maps
Upon search, the system SHALL display the top 3 fastest routes using Google Maps iframe embeds.

### REQ-FE-003: Carrier List
The system SHALL render a list of carriers returned from the backend API, showing carrier name and trucks per day.

### REQ-FE-004: API Integration
The frontend SHALL send search requests to `POST /api/search` with `{ from_city, to_city }`.
