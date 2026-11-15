# NASA data integration and ML context

AgriSpace connects to the NASA POWER Daily Point API when `NASA_POWER_ENABLED=true`. The connector queries the Agroclimatology community with temperature, corrected precipitation, relative humidity, solar radiation, and wind parameters, requests UTC, applies bounded retries, and caches responses for 15 minutes. NASA POWER’s daily service returns analysis-ready time-series data; NASA documents that daily data may be requested from 1981 to near-real-time, and warns clients not to repeatedly request the same grid location. [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) [NASA POWER API overview](https://power.larc.nasa.gov/docs/services/api/)

The integration preserves source, product/version (when supplied), retrieval time, spatial coverage, units, availability, cache status, quality note, and `simulated` state. When no live connection is enabled, the payload is named `AgriSpace simulated dataset`; it never claims to be NASA output.

## LLM context

`GET /api/v1/farms/{farm_id}/llm-context` returns a bounded structured fact bundle: farm attributes, the source-labelled environmental payload, and safety rules that prohibit silently filling gaps or presenting a recommendation as a guarantee. It does not call an external LLM and it does not send user data to a model provider.

## ML use

NASA climate observations are potential **features**, not training labels. A yield/suitability model also needs real field-level crop outcomes, consistent crop/management records, data licences, a temporal and spatial validation plan, and expert approval. The training readiness gate rejects simulated data and incomplete provenance. See [ML training governance](ml/training-governance.md).

Future sources such as SMAP and GPM IMERG should be integrated through separate adapters because their access, spatial/temporal resolution, quality flags, and Earthdata requirements differ. NASA’s POWER documentation provides parameter/temporal availability; do not substitute one product for another without recording it. [NASA POWER communities and sources](https://power.larc.nasa.gov/docs/methodology/communities/)
