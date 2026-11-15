# API security contract

## Authentication and errors

Protected API calls use `Authorization: Bearer <access-token>`. Missing, expired, or invalid tokens return `401`; a valid identity without resource access returns `403`; absent resources return `404`. Responses do not reveal whether a login email exists beyond the login endpoint’s generic invalid-credential message.

## Authorization matrix

| Resource | Farmer | Agronomist | Administrator |
|---|---|---|---|
| Own farms / fields | Create, read, update, delete | No access until assignments exist | Read/update as current implementation permits |
| Another farmer's farm | Denied | Denied until assignment feature is built | Allowed |
| Climate / rotation data | Own farms only | Assignment required (pending) | Allowed |

## Secure integration rules

- Keep NASA and Maps credentials in server/edge environment variables, never in React bundles.
- Label source, product, units, observed date, retrieval time, quality status, and simulation status for every environmental response.
- Use outbound timeouts, retries with jitter, response-size limits, and allowlisted base URLs for every connector.
- Do not train or serve a model unless its artifact, validation report, dataset provenance, and limitations are present.
