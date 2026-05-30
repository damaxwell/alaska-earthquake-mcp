import json
import xml.etree.ElementTree as ET

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Alaska Earthquake MCP")

FDSN_BASE = "http://dispatchon.aec.alaska.edu/fdsnws/event/1/query"

# QuakeML namespaces
NS = {
    "q": "http://quakeml.org/xmlns/quakeml/1.2",
    "b": "http://quakeml.org/xmlns/bed/1.2",
}


def _text(element, path):
    node = element.find(path, NS)
    return node.text if node is not None else None


def _parse_quakeml(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    events = []
    for event in root.findall(".//b:event", NS):
        origin = event.find(".//b:origin", NS)
        magnitude = event.find(".//b:magnitude", NS)
        events.append({
            "id": event.get("publicID", "").split("/")[-1],
            "description": _text(event, ".//b:description/b:text"),
            "time": _text(origin, "b:time/b:value") if origin is not None else None,
            "latitude": _text(origin, "b:latitude/b:value") if origin is not None else None,
            "longitude": _text(origin, "b:longitude/b:value") if origin is not None else None,
            "depth_m": _text(origin, "b:depth/b:value") if origin is not None else None,
            "magnitude": _text(magnitude, "b:mag/b:value") if magnitude is not None else None,
            "magnitude_type": _text(magnitude, "b:type") if magnitude is not None else None,
        })
    return events


@mcp.tool()
def query_earthquakes(
    starttime: str,
    endtime: str,
    latitude: float,
    longitude: float,
    maxradius: float,
) -> str:
    """Query the Alaska Earthquake Center FDSN catalog and return a JSON list of events.

    Each event includes: id, description, time, latitude, longitude, depth_m,
    magnitude, and magnitude_type.

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
        "nodata": "404",
    }
    response = httpx.get(FDSN_BASE, params=params, timeout=30)
    response.raise_for_status()
    events = _parse_quakeml(response.text)
    return json.dumps(events, indent=2)
