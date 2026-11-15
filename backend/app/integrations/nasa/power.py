"""NASA POWER connector with provenance, bounded retries, and an explicit demo mode."""
import asyncio
from datetime import date, datetime, timedelta, timezone
from time import monotonic
import httpx
from app.core.config import get_settings

_cache: dict[str, tuple[float, dict]] = {}
CACHE_SECONDS = 900
POWER_PARAMETERS = "T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M"

async def daily_weather(latitude: float, longitude: float, days: int = 14) -> dict:
    settings = get_settings()
    cache_key = f"{latitude:.4f}:{longitude:.4f}:{days}:{settings.nasa_power_enabled}"
    cached = _cache.get(cache_key)
    if cached and monotonic() - cached[0] < CACHE_SECONDS: return {**cached[1], "cache_status": "hit"}
    if not settings.nasa_power_enabled:
        result = demo_weather(days)
    else:
        result = await _fetch_power(latitude, longitude, days)
    _cache[cache_key] = (monotonic(), result)
    return {**result, "cache_status": "miss"}

async def _fetch_power(latitude: float, longitude: float, days: int) -> dict:
    settings = get_settings(); end, start = date.today() - timedelta(days=1), date.today() - timedelta(days=days)
    params = {"parameters": POWER_PARAMETERS, "community": "AG", "longitude": longitude, "latitude": latitude, "start": start.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"), "format": "JSON", "time-standard": "UTC"}
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(15, connect=5)) as client:
                response = await client.get(settings.nasa_power_base_url, params=params)
                response.raise_for_status()
            return _normalize_power(response.json(), latitude, longitude)
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            last_error = error
            if attempt < 2: await asyncio.sleep(0.5 * (2 ** attempt))
    # Never replace an unavailable live request with NASA-labelled dummy data.
    return {"source": "NASA POWER", "product": "POWER Daily API", "simulated": False, "available": False, "error": "NASA POWER data is temporarily unavailable; no observations were substituted.", "retrieved_at": datetime.now(timezone.utc).isoformat(), "data": [], "request": {"latitude": latitude, "longitude": longitude}, "error_class": type(last_error).__name__ if last_error else "UnknownError"}

def _normalize_power(payload: dict, latitude: float, longitude: float) -> dict:
    properties = payload["properties"]; parameters = properties["parameter"]
    dates = sorted(parameters.get("T2M", {}).keys())
    def value(parameter: str, day: str):
        raw = parameters.get(parameter, {}).get(day)
        return None if raw in (None, -999, -999.0) else raw
    observations = [{"date": f"{day[:4]}-{day[4:6]}-{day[6:]}", "temperature_c": value("T2M", day), "rainfall_mm": value("PRECTOTCORR", day), "relative_humidity_pct": value("RH2M", day), "solar_radiation_kwh_m2_day": value("ALLSKY_SFC_SW_DWN", day), "wind_speed_m_s": value("WS2M", day), "soil_moisture_pct": None} for day in dates]
    return {"source": "NASA POWER", "product": "POWER Daily API", "product_version": payload.get("header", {}).get("api", {}).get("version"), "simulated": False, "available": True, "retrieved_at": datetime.now(timezone.utc).isoformat(), "spatial_coverage": {"type": "point", "latitude": latitude, "longitude": longitude}, "units": {"temperature_c": "°C", "rainfall_mm": "mm/day", "relative_humidity_pct": "%", "solar_radiation_kwh_m2_day": "kWh/m²/day", "wind_speed_m_s": "m/s"}, "quality_note": "NASA POWER point-grid environmental data; interpret at product spatial resolution, not as in-field sensor readings.", "data": observations}

def demo_weather(days: int) -> dict:
    today = date.today(); observations = []
    for offset in range(days - 1, -1, -1):
        observed = today - timedelta(days=offset)
        observations.append({"date": observed.isoformat(), "temperature_c": round(27 + ((offset % 5) - 2) * .7, 1), "rainfall_mm": round(max(0, 8 - (offset % 6) * 1.1), 1), "relative_humidity_pct": round(63 + (offset % 5) * 2, 1), "solar_radiation_kwh_m2_day": round(4.5 + (offset % 3) * .3, 1), "wind_speed_m_s": round(2.3 + (offset % 3) * .2, 1), "soil_moisture_pct": round(34 + (offset % 4) * 1.2, 1)})
    return {"source": "AgriSpace simulated dataset", "product": "Demo environmental observations", "simulated": True, "available": True, "retrieved_at": datetime.now(timezone.utc).isoformat(), "spatial_coverage": {"type": "point", "note": "Synthetic development data"}, "units": {"temperature_c": "°C", "rainfall_mm": "mm/day", "soil_moisture_pct": "%"}, "quality_note": "Not a NASA measurement. Use for interface and API testing only.", "data": observations}
