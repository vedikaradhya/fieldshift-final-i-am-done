# Security architecture and operations

## Security posture

AgriSpace treats farm boundaries, crop history, soil profiles, contact details, and access tokens as sensitive data. The system follows deny-by-default access control: an authenticated identity must own a farm (or be an authorized administrator) before any farm, field, climate, or recommendation endpoint responds.

## Implemented controls

- **Password protection:** passwords are hashed with Argon2id; plaintext passwords are neither logged nor stored.
- **Authentication:** short-lived signed JWT access tokens. Every protected route resolves the token to a current database user.
- **Authorization:** farm ownership is rechecked server-side. Field authorization flows through its parent farm, preventing insecure direct-object references.
- **Input safety:** Pydantic validates request types and field limits. GeoJSON polygons must be closed, structurally valid, and within geographic coordinate ranges.
- **Transport/browser hardening:** responses set `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and `Cross-Origin-Resource-Policy`. HSTS is added on HTTPS requests.
- **Abuse resistance:** authentication endpoints are rate-limited (8 requests per client per 60 seconds in the local profile); request bodies are capped at 1 MB.
- **CORS:** origins come from `CORS_ORIGINS`; credentials are allowed only to explicitly configured origins.
- **Data provenance:** demo environmental measurements are tagged `simulated: true` and named as simulated, avoiding unsafe scientific claims.

## Threat model

| Threat | Primary mitigation | Operational requirement |
|---|---|---|
| Credential stuffing | Auth rate limit, Argon2id | Replace local limiter with Redis; alert on spikes |
| Token theft | Short token lifetime, HTTPS | Use HttpOnly Secure refresh cookies and token revocation table |
| Cross-farm data disclosure | Owner check on each resource | Add collaborator grants and authorization tests before enabling sharing |
| SQL injection | SQLAlchemy parameterized queries | Avoid raw SQL; review any spatial SQL |
| XSS | JSON API, browser headers | Add a strict frontend CSP at Nginx and escape all future rich text |
| Malicious uploads | Not yet enabled | Virus scanning, object-store isolation, signed URLs, MIME verification |
| NASA/API outage | Explicit demo fallback; no fabricated data | Retries, circuit breaker, source-health monitoring |

## Production deployment checklist

1. Set a unique, high-entropy `SECRET_KEY` of at least 32 bytes through a secret manager; never commit it.
2. Terminate TLS at Nginx/load balancer, redirect HTTP to HTTPS, and enable HSTS only after HTTPS is verified.
3. Use PostgreSQL/PostGIS with a restricted application role; enable automated encrypted backups and recovery drills.
4. Replace SQLite startup schema creation with reviewed Alembic migrations.
5. Move rate limiting, refresh-token revocation, Celery jobs, and cache state to Redis with authentication/TLS.
6. Set `CORS_ORIGINS` to exact application origins—never `*` with credentials.
7. Add CSP, `connect-src` allowlists, and Google Maps domain/API restrictions at the edge.
8. Use an email provider for verification/reset tokens that are single-use, hashed at rest, and expiry-bound.
9. Centralize structured audit events without passwords, tokens, farm geometries, or personally identifying values in logs.
10. Run dependency scanning, SAST, secret scanning, migration tests, and authorization tests in CI.

## Incident response

1. **Triage:** preserve logs, affected request IDs, and timestamps. Do not copy secrets or raw boundaries into tickets.
2. **Contain:** rotate affected credentials, revoke refresh sessions, disable compromised API keys, and restrict exposed origins.
3. **Eradicate:** patch the root cause, add a regression test, and deploy through the normal reviewed release path.
4. **Recover:** validate authorization controls, monitor error/authentication rates, and notify affected users where required by law.
5. **Learn:** document the timeline, impact, and preventive actions in the security review.

## Known gaps before production

Refresh-token cookies, CSRF protection for cookie-authenticated requests, account recovery, MFA, audit-event persistence, Redis rate limiting, security monitoring, and formal penetration testing are not yet implemented. They are mandatory gates for a production launch.
