from typing import Dict, Literal

import httpx  # type: ignore[reportMissingModuleSource]
from mcp.server.fastmcp import FastMCP  # type: ignore[reportMissingModuleSource]

# Create MCP server
mcp = FastMCP(name="WeatherAgent", stateless_http=True)

# Export ASGI app for uvicorn
app = mcp.streamable_http_app()


def _units_to_open_meteo(units: Literal["metric", "imperial"]) -> Dict[str, str]:
    if units == "imperial":
        return {"temperature_unit": "fahrenheit", "wind_speed_unit": "mph"}
    return {"temperature_unit": "celsius", "wind_speed_unit": "kmh"}


@mcp.tool()
def weather(query: str, units: Literal["metric", "imperial"] = "metric") -> Dict:
    """Get current weather for a place name using Open-Meteo.

    - query: City or place name (e.g. "Karachi", "New York, US").
    - units: "metric" or "imperial".
    """
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_url = "https://api.open-meteo.com/v1/forecast"

    with httpx.Client(timeout=10.0) as client:
        georesp = client.get(geocode_url, params={"name": query, "count": 1, "language": "en", "format": "json"})
        georesp.raise_for_status()
        geodata = georesp.json()
        if not geodata or not geodata.get("results"):
            raise ValueError(f"No location found for '{query}'")

        loc = geodata["results"][0]
        latitude = loc["latitude"]
        longitude = loc["longitude"]

        unit_params = _units_to_open_meteo(units)

        cur_params = {
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

        wxresp = client.get(forecast_url, params=cur_params)
        wxresp.raise_for_status()
        wx = wxresp.json()

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

