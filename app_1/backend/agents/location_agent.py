"""
LocationAgent: Resolves area names (G-13, F-10, Bahria Town) to coordinates.
Uses LOCATION_MAP for known areas, Gemini for ambiguous locations.
"""
import math
from datetime import datetime
from typing import Optional

from backend.data.providers import LOCATION_MAP


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km between two coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class LocationAgent:
    """
    Agent 3: Resolves location names to coordinates and calculates distances.
    """

    def __init__(self, gemini_model=None):
        self.model = gemini_model
        self.agent_name = "LocationAgent"
        # Default center: Islamabad
        self.default_lat = 33.6844
        self.default_lng = 73.0479

    def run(self, intent: dict, trace_log: list) -> dict:
        """Resolve location from intent and return coordinates."""
        start = datetime.utcnow().isoformat()
        location_str = intent.get("location") or ""

        resolved = self._resolve_location(location_str)

        result = {
            "original": location_str,
            "resolved_name": resolved["full_name"],
            "lat": resolved["lat"],
            "lng": resolved["lng"],
            "resolution_method": resolved["method"],
        }

        trace_log.append({
            "timestamp": start,
            "agent": self.agent_name,
            "action": f"Resolved location '{location_str}' to coordinates",
            "tool": "location_map_lookup",
            "reasoning": (
                f"Searched LOCATION_MAP for '{location_str}'. "
                f"Found: {resolved['full_name']} at ({resolved['lat']:.4f}, {resolved['lng']:.4f}). "
                f"Method: {resolved['method']}"
            ),
            "output": result
        })

        return result

    def _resolve_location(self, location_str: str) -> dict:
        """Attempt to resolve location string to coordinates."""
        if not location_str:
            return {"lat": self.default_lat, "lng": self.default_lng,
                    "full_name": "Islamabad (default)", "method": "default"}

        # Normalize
        key = location_str.lower().strip().replace(",", "").replace("islamabad", "").strip()

        # Direct lookup
        if key in LOCATION_MAP:
            loc = LOCATION_MAP[key]
            return {**loc, "method": "exact_match"}

        # Partial match
        for map_key, loc in LOCATION_MAP.items():
            if map_key in key or key in map_key:
                return {**loc, "method": "partial_match"}

        # Try extracting sector pattern like G-13, F-10
        import re
        sector_match = re.search(r'([A-HI])-?(\d{1,2})', location_str, re.IGNORECASE)
        if sector_match:
            normalized = f"{sector_match.group(1).upper()}-{sector_match.group(2)}"
            lookup_key = normalized.lower()
            if lookup_key in LOCATION_MAP:
                return {**LOCATION_MAP[lookup_key], "method": "sector_parse"}
            # Estimate: use Islamabad center with slight offset
            return {
                "lat": self.default_lat + (int(sector_match.group(2)) - 13) * 0.01,
                "lng": self.default_lng + 0.005,
                "full_name": f"{normalized}, Islamabad",
                "method": "sector_estimate"
            }

        # Fallback
        return {
            "lat": self.default_lat,
            "lng": self.default_lng,
            "full_name": location_str or "Islamabad",
            "method": "fallback"
        }

    def calculate_distances(self, user_lat: float, user_lng: float, providers: list) -> list:
        """Add distance_km to each provider."""
        for p in providers:
            p["distance_km"] = round(haversine_distance(user_lat, user_lng, p["lat"], p["lng"]), 2)
        return providers
