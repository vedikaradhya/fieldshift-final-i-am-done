# AgriSpace

AgriSpace is a modular smart-farming platform for environmental context, farm boundaries, and explainable crop-rotation guidance. It is intentionally transparent about data provenance: the included local configuration runs in **demo mode**, and no simulated value is described as a NASA observation.

## What is working now

- FastAPI OpenAPI service at `http://localhost:8000/docs`
- Argon2id password hashing and short-lived JWT access tokens
- User-scoped farm CRUD, GeoJSON boundary validation, and area calculation
- NASA POWER adapter interface with an explicit simulated-data fallback
- Configurable, constraint-aware crop rotation scoring API
- Field CRUD guarded through parent-farm authorization
- Apple-inspired React dashboard login, selected-farm conditions, source disclosure, and responsive layout
- API tests for registration, area calculation, field ownership, security headers, and cross-user isolation

## Security

The local API includes Argon2id password hashing, JWT validation, user-scoped resource authorization, authentication throttling, request-size limits, and browser-facing security headers. See the [security architecture](docs/security/security-architecture.md) and [API security contract](docs/security/api-security.md) for the operating model, threat model, production checklist, and known launch blockers.

## NASA and ML context

Set `NASA_POWER_ENABLED=true` to request source-labelled NASA POWER daily environmental data. The `GET /api/v1/farms/{farm_id}/llm-context` endpoint returns a structured, provenance-preserving fact bundle for a future LLM integration, without invoking an external LLM or transmitting farm data. Read [NASA integration](docs/nasa-integration.md) and [ML training governance](docs/ml/training-governance.md) before enabling a model workflow.

## Run locally

```bash
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Docker Compose remains available as an optional containerised setup with `docker compose up --build`; it is not required for local deployment.

### Deployment launchers

For local deployment without Docker, set a unique `SECRET_KEY` (at least 32 random bytes) in `.env`, then run `./start.sh` on macOS/Linux or `start.bat` on Windows. The launchers provision Python dependencies, install frontend packages when missing, start the API and web app in the background, and refuse the sample key before starting.

Register through `POST /api/v1/auth/register` in the OpenAPI UI, then sign into the web app. The frontend does not ship secrets. To enable the NASA POWER adapter, set `NASA_POWER_ENABLED=true`; production deployment must set a unique `SECRET_KEY`, configure HTTPS cookies/refresh tokens, PostgreSQL/PostGIS, Redis/Celery, rate limiting, and an email provider.

## Requirement status

Implemented as a working foundation: Phase 1, the core Phase 2 login path, and a Phase 3/4/7 vertical slice. Deliberately pending: email delivery/verification, refresh-cookie session lifecycle, Google OAuth/MFA, Terra Draw/Google Maps UI, PostGIS migration, background workers, production NASA products beyond POWER, persistent observations, ML training/governance, collaborator roles, admin/ agronomist workspace, reports, and comprehensive E2E/security suites. These require further implementation and, for some integrations, credentials and validated datasets.
