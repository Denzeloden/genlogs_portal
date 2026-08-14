# GenLogs Platform — Architecture

## Module Flow

```mermaid
flowchart TB
  subgraph ingestion [Capture and Ingestion]
    Cameras[Trident Sensors]
    Gateway[Image Gateway]
    Queue[Message Queue]
  end

  subgraph processing [AI and Enrichment]
    VisionAI[Vision AI Worker]
    Enrichment[Enrichment Service]
    FMCSA[SAFER FMCSA API]
  end

  subgraph portal [Web Portal Prototype Scope]
    React[React Web Portal]
    FastAPI[FastAPI Main Server]
    Postgres[(PostgreSQL)]
  end

  Cameras --> Gateway --> Queue --> VisionAI
  VisionAI --> Enrichment --> FMCSA
  Enrichment --> FastAPI --> Postgres
  React -->|"POST /api/search"| FastAPI
  FastAPI -->|"aggregate sightings"| Postgres
  FastAPI --> React
  React --> GoogleMaps[Google Maps Embed]
```

## Prototype Scope

This prototype implements the **User Query → Data Retrieval → Display** path. Ingestion, Vision AI, and live FMCSA calls are simulated via seeded PostgreSQL data.

## Components

| Component | Role |
|-----------|------|
| React Web Portal | City search UI, route maps, carrier list |
| FastAPI Main Server | Search API, health check, static file serving |
| PostgreSQL | Stores carriers, vehicles, sightings |
| Google Maps Embed | Displays top 3 route options |
