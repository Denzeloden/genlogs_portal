# GenLogs Portal — Deployment Spec

## Requirements

### REQ-DEP-001: Heroku Procfile
The system SHALL include a Procfile with web and release phases.

### REQ-DEP-002: Buildpacks
The system SHALL use Node.js and Python buildpacks for single-dyno deployment.

### REQ-DEP-003: Database Migrations
The release phase SHALL run Alembic migrations and seed mock data.

### REQ-DEP-004: Environment
The system SHALL use DATABASE_URL for PostgreSQL connection (Heroku Postgres addon).
