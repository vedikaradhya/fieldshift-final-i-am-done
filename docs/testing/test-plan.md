# Test plan

| ID | Scenario | Automated |
|---|---|---|
| AUTH-001 | Register with strong credentials | Yes |
| FARM-001 | Persist valid GeoJSON farm and calculate area | Yes |
| SEC-001 | Deny cross-user farm access | Yes |
| DATA-001 | Clearly label unconfigured data integration as simulated | Yes (health disclosure) |

Future integration tests require configured PostGIS, Redis, and NASA test fixtures. No live NASA call is made during tests.
