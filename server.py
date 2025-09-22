from typing import Dict, Literal, Tuple, Any
import os
import time
import logging

import httpx  # type: ignore[reportMissingModuleSource]
from mcp.server.fastmcp import FastMCP  # type: ignore[reportMissingModuleSource]

# Create MCP server
mcp = FastMCP(name="WeatherAgent", stateless_http=True)

# Export ASGI app for uvicorn
app = mcp.streamable_http_app()


# --- Configuration & Logging ---
SERVICE_NAME = "WeatherAgent"
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10.0"))
HTTP_MAX_RETRIES = int(os.getenv("HTTP_MAX_RETRIES", "2"))  # total attempts = retries + 1
HTTP_BACKOFF_SECONDS = float(os.getenv("HTTP_BACKOFF_SECONDS", "0.5"))
GEOCODE_CACHE_TTL_SECONDS = int(os.getenv("GEOCODE_CACHE_TTL_SECONDS", "3600"))  # 1 hour
FORECAST_CACHE_TTL_SECONDS = int(os.getenv("FORECAST_CACHE_TTL_SECONDS", "300"))  # 5 minutes

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(SERVICE_NAME)


# --- Simple in-memory TTL caches (process-local) ---
_geocode_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_forecast_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _cache_get(cache: Dict[str, Tuple[float, Dict[str, Any]]], key: str, ttl_seconds: int) -> Dict[str, Any] | None:
    now = time.time()
    entry = cache.get(key)
    if not entry:
        return None
    ts, data = entry
    if now - ts > ttl_seconds:
        cache.pop(key, None)
        return None
    return data


def _cache_set(cache: Dict[str, Tuple[float, Dict[str, Any]]], key: str, data: Dict[str, Any]) -> None:
    cache[key] = (time.time(), data)


def _units_to_open_meteo(units: Literal["metric", "imperial"]) -> Dict[str, str]:
    if units == "imperial":
        return {"temperature_unit": "fahrenheit", "wind_speed_unit": "mph"}
    return {"temperature_unit": "celsius", "wind_speed_unit": "kmh"}


def _http_get_with_retry(client: httpx.Client, url: str, *, params: Dict[str, Any]) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(HTTP_MAX_RETRIES + 1):
        try:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            return resp
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:  # type: ignore[attr-defined]
            last_exc = exc
            if attempt < HTTP_MAX_RETRIES:
                sleep_for = HTTP_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "GET %s failed (attempt %d/%d): %s; backing off %.2fs",
                    url,
                    attempt + 1,
                    HTTP_MAX_RETRIES + 1,
                    exc,
                    sleep_for,
                )
                time.sleep(sleep_for)
            else:
                break
    assert last_exc is not None
    raise last_exc


@mcp.tool()
def weather(query: str, units: Literal["metric", "imperial"] = "metric") -> Dict[str, Any]:
    """Get current weather for a place name using Open-Meteo.

    - query: City or place name (e.g. "Karachi", "New York, US").
    - units: "metric" or "imperial".
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("'query' must be a non-empty string")
    query = query.strip()

    if units not in ("metric", "imperial"):
        raise ValueError("'units' must be either 'metric' or 'imperial'")

    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_url = "https://api.open-meteo.com/v1/forecast"

    # --- Geocoding with cache ---
    geocode_key = f"{query.lower()}|en"
    geodata = _cache_get(_geocode_cache, geocode_key, GEOCODE_CACHE_TTL_SECONDS)

    headers = {
        "User-Agent": f"{SERVICE_NAME}/{SERVICE_VERSION} (+https://example.invalid)"
    }

    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, headers=headers) as client:
        if geodata is None:
            geo_params: Dict[str, Any] = {"name": query, "count": 1, "language": "en", "format": "json"}
            georesp = _http_get_with_retry(client, geocode_url, params=geo_params)
            geodata = georesp.json()
            if geodata:
                _cache_set(_geocode_cache, geocode_key, geodata)

        if not geodata or not geodata.get("results"):
            raise ValueError(f"No location found for '{query}'")

        loc = geodata["results"][0]
        latitude = loc["latitude"]
        longitude = loc["longitude"]

        unit_params = _units_to_open_meteo(units)

        cur_params: Dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join([
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
            ]),
            **unit_params,
        }

        # --- Forecast with cache ---
        forecast_key = f"{latitude:.4f},{longitude:.4f}|{units}"
        wx = _cache_get(_forecast_cache, forecast_key, FORECAST_CACHE_TTL_SECONDS)
        if wx is None:
            wxresp = _http_get_with_retry(client, forecast_url, params=cur_params)
            wx = wxresp.json()
            if wx:
                _cache_set(_forecast_cache, forecast_key, wx)

    return {
        "location": {
            "name": loc.get("name"),
            "country": loc.get("country"),
            "admin1": loc.get("admin1"),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": wx.get("timezone"),
        },
        "units": units,
        "current": wx.get("current"),
    }


@mcp.tool()
def health() -> Dict[str, Any]:
    """Basic health and version info for readiness/liveness probes."""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "ok",
        "time": int(time.time()),
    }


if __name__ == "__main__":
    # Local/dev runner: uvicorn server:app --host 0.0.0.0 --port 8000
    import uvicorn  # type: ignore[reportMissingModuleSource]

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        log_level=log_level.lower(),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )

