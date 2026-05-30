import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Alaska Earthquake MCP")

FDSN_BASE = "http://dispatchon.aec.alaska.edu/fdsnws/event/1/query"


@mcp.tool()
def query_earthquakes(
    starttime: str,
    endtime: str,
    latitude: float,
    longitude: float,
    maxradius: float,
) -> str:
    """Query the Alaska Earthquake Center FDSN catalog and return raw QuakeML XML.

    Args:
        starttime: Start of time window in ISO 8601 format (e.g. 2026-03-01T00:00:00)
        endtime: End of time window in ISO 8601 format (e.g. 2026-04-01T00:00:00)
        latitude: Center latitude for radius search (decimal degrees)
        longitude: Center longitude for radius search (decimal degrees)
        maxradius: Maximum radius from center point (decimal degrees)
    """
    params = {
        "starttime": starttime,
        "endtime": endtime,
        "latitude": latitude,
        "longitude": longitude,
        "maxradius": maxradius,
        "formatted": "true",
        "nodata": "404",
    }
    response = httpx.get(FDSN_BASE, params=params, timeout=30)
    response.raise_for_status()
    return response.text
