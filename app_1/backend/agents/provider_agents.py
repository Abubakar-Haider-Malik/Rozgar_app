"""
ProviderDiscoveryAgent: Finds nearby providers matching the service type.
RankingAgent: Scores providers based on distance, rating, availability, urgency.
"""
import copy
from datetime import datetime
from typing import List

from backend.data.providers import PROVIDERS
from backend.agents.location_agent import LocationAgent


class ProviderDiscoveryAgent:
    """
    Agent 4: Discovers providers matching the requested service category.
    Filters by category, calculates distances, returns candidates.
    """

    def __init__(self):
        self.agent_name = "ProviderDiscoveryAgent"
        self.location_agent = LocationAgent()

    def run(self, intent: dict, location_info: dict, trace_log: list) -> List[dict]:
        start = datetime.utcnow().isoformat()
        service_type = intent.get("service_type", "")

        # Filter by category (case-insensitive)
        candidates = [
            copy.deepcopy(p) for p in PROVIDERS
            if p["category"].lower() == service_type.lower()
        ]

        if not candidates:
            # Return all providers if no category match (fallback)
            candidates = copy.deepcopy(PROVIDERS[:10])

        # Add distances from user location
        user_lat = location_info.get("lat", 33.6844)
        user_lng = location_info.get("lng", 73.0479)
        candidates = self.location_agent.calculate_distances(user_lat, user_lng, candidates)

        # Filter to within 20km radius
        nearby = [p for p in candidates if p.get("distance_km", 999) <= 20]
        if not nearby:
            nearby = candidates  # if none within 20km, return all

        # Sort by distance initially
        nearby.sort(key=lambda x: x.get("distance_km", 999))

        trace_log.append({
            "timestamp": start,
            "agent": self.agent_name,
            "action": f"Discovered {len(nearby)} providers for '{service_type}'",
            "tool": "mock_provider_database",
            "reasoning": (
                f"Queried database for category='{service_type}'. "
                f"Found {len(candidates)} total, {len(nearby)} within 20km of "
                f"{location_info.get('resolved_name', 'user location')}."
            ),
            "output": {
                "total_found": len(nearby),
                "service_type": service_type,
                "location": location_info.get("resolved_name"),
                "providers_preview": [p["name"] for p in nearby[:5]]
            }
        })

        return nearby


class RankingAgent:
    """
    Agent 5: Scores and ranks providers.
    Score = weighted sum of distance, rating, availability, urgency match.
    """

    def __init__(self):
        self.agent_name = "RankingAgent"

    def run(self, providers: list, intent: dict, trace_log: list) -> list:
        start = datetime.utcnow().isoformat()
        urgency = intent.get("urgency", "flexible")
        time_pref = intent.get("time_preference")

        scored = []
        for p in providers:
            score, reasoning = self._score_provider(p, urgency, time_pref)
            p["score"] = round(score, 3)
            p["ranking_reason"] = reasoning
            scored.append(p)

        # Sort descending by score
        scored.sort(key=lambda x: x["score"], reverse=True)

        # Add rank position
        for i, p in enumerate(scored):
            p["rank"] = i + 1

        trace_log.append({
            "timestamp": start,
            "agent": self.agent_name,
            "action": f"Ranked {len(scored)} providers by composite score",
            "tool": "ranking_algorithm",
            "reasoning": (
                f"Applied scoring: 40% rating + 30% proximity + 20% response_time + 10% verified_bonus. "
                f"Urgency='{urgency}' increased weight on response_time. "
                f"Top provider: {scored[0]['name'] if scored else 'N/A'} (score={scored[0]['score'] if scored else 0})"
            ),
            "output": {
                "top_3": [
                    {"rank": p["rank"], "name": p["name"], "score": p["score"], "reason": p["ranking_reason"]}
                    for p in scored[:3]
                ]
            }
        })

        return scored

    def _score_provider(self, provider: dict, urgency: str, time_pref: str) -> tuple:
        """Compute composite score with explanation."""
        # Normalize rating (0–5 → 0–1)
        rating_score = provider.get("rating", 3.0) / 5.0

        # Proximity score (0–20km → 1–0)
        dist = provider.get("distance_km", 10)
        proximity_score = max(0, 1 - (dist / 20))

        # Response time score (lower = better, normalize to 0–1)
        resp = provider.get("response_time_min", 60)
        response_score = max(0, 1 - (resp / 120))

        # Verified bonus
        verified_bonus = 0.1 if provider.get("verified") else 0.0

        # Availability score: more slots = better
        slots = len(provider.get("available_slots", []))
        availability_score = min(slots / 5, 1.0)

        # Urgency multiplier: if urgent, response_time matters 2x
        urgency_multiplier = 2.0 if urgency == "urgent" else 1.0

        # Weighted composite
        score = (
            0.35 * rating_score +
            0.25 * proximity_score +
            0.20 * response_score * urgency_multiplier +
            0.10 * availability_score +
            verified_bonus
        )
        # Normalize to 0–1 range
        score = min(score, 1.0)

        reasoning = (
            f"Rating={provider['rating']}/5 (+{rating_score:.2f}), "
            f"Distance={dist}km (+{proximity_score:.2f}), "
            f"Response={resp}min (+{response_score:.2f}×{urgency_multiplier}urgency), "
            f"Verified={'✓' if provider.get('verified') else '✗'}"
        )

        return score, reasoning
