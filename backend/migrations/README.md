# Database migrations

The initial ORM schema is created at startup for the development profile. Production deployments should run Alembic migrations before starting the API. PostGIS uses `geometry(Geometry, 4326)` for `farms.boundary` and `fields.boundary`; the current SQLite demo stores validated GeoJSON so the application remains runnable without PostGIS.
