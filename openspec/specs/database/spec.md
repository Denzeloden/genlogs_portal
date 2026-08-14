# GenLogs Portal — Database Spec

## Requirements

### REQ-DB-001: Carriers Table
The system SHALL store carrier records in `carriers` with id, dot_number, name, mc_number, last_fmcsa_sync.

### REQ-DB-002: Vehicles Table
The system SHALL store vehicle records in `vehicles` linked to carriers via carrier_id.

### REQ-DB-003: Sightings Table
The system SHALL store sighting records in `sightings` with origin_city_inferred, dest_city_inferred, and vehicle_id FK.

### REQ-DB-004: Indexes
The system SHALL index sightings on origin_city_inferred and dest_city_inferred, and carriers on dot_number.

### REQ-DB-005: Seed Data
The system SHALL seed mock data matching Route A, B, and C carrier volume rules.
