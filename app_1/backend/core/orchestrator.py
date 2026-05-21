"""
KaamKar AI Orchestrator — Antigravity Core.

This is the central multi-agent orchestration layer.
It coordinates all 8 agents in sequence:
  IntentAgent → LocationAgent → ProviderDiscoveryAgent →
  RankingAgent → BookingAgent → NotificationAgent → FollowUpAgent

Each agent appends its reasoning to a shared trace_log.
The orchestrator manages state transitions and handles failures gracefully.
"""
import os
import json
from datetime import datetime
from typing import Optional
import logging

import google.generativeai as genai

from backend.agents.intent_agent import IntentAgent
from backend.agents.location_agent import LocationAgent
from backend.agents.provider_agents import ProviderDiscoveryAgent, RankingAgent
from backend.agents.booking_agents import BookingAgent, NotificationAgent, FollowUpAgent

logger = logging.getLogger(__name__)


class KaamKarOrchestrator:
    """
    Central orchestration engine powered by Antigravity principles:
    - Plan → Reason → Decide → Act → Follow-up
    - Each agent is autonomous but coordinated
    - Full trace logging at every step
    - Graceful degradation when APIs are unavailable
    """

    WORKFLOW_STAGES = [
        "intent_extraction",
        "location_resolution",
        "provider_discovery",
        "provider_ranking",
        "booking",
        "notification",
        "followup",
    ]

    def __init__(self):
        self._init_gemini()
        self._init_agents()

    def _init_gemini(self):
        """Initialize Gemini API client."""
        api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Gemini API init failed: {e}. Using heuristics fallback.")
        else:
            logger.info("No GEMINI_API_KEY found. Running with heuristic NLP only.")

    def _init_agents(self):
        """Instantiate all agents."""
        self.intent_agent = IntentAgent(gemini_model=self.gemini_model)
        self.location_agent = LocationAgent(gemini_model=self.gemini_model)
        self.discovery_agent = ProviderDiscoveryAgent()
        self.ranking_agent = RankingAgent()
        self.booking_agent = BookingAgent()
        self.notification_agent = NotificationAgent()
        self.followup_agent = FollowUpAgent()

    def process_request(self, user_text: str) -> dict:
        """
        Main orchestration pipeline.
        Takes raw user text, runs all agents, returns full result with traces.
        """
        session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        trace_log = []
        pipeline_start = datetime.utcnow().isoformat()

        # ── Orchestrator planning log ──
        trace_log.append({
            "timestamp": pipeline_start,
            "agent": "Orchestrator",
            "action": "Pipeline initiated — planning agent workflow",
            "tool": "kaamkar_orchestrator",
            "reasoning": (
                f"Received user request: '{user_text[:100]}'. "
                f"Initiating {len(self.WORKFLOW_STAGES)}-stage agentic workflow: "
                + " → ".join(self.WORKFLOW_STAGES)
            ),
            "output": {"session_id": session_id, "stages": self.WORKFLOW_STAGES}
        })

        try:
            # ── Stage 1: Intent Extraction ──
            intent = self.intent_agent.run(user_text, trace_log)

            # ── Stage 2: Location Resolution ──
            location_info = self.location_agent.run(intent, trace_log)

            # ── Stage 3: Provider Discovery ──
            providers = self.discovery_agent.run(intent, location_info, trace_log)

            if not providers:
                return self._no_providers_response(intent, location_info, trace_log, session_id)

            # ── Stage 4: Ranking ──
            ranked_providers = self.ranking_agent.run(providers, intent, trace_log)

            # ── Stage 5: Booking ──
            top_provider = ranked_providers[0]
            booking = self.booking_agent.run(top_provider, intent, trace_log)

            # ── Stage 6: Notifications ──
            notifications = self.notification_agent.run(booking, intent, trace_log)

            # ── Stage 7: Follow-up ──
            followup = self.followup_agent.run(booking, intent, trace_log)

            # ── Final orchestrator summary ──
            trace_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "Orchestrator",
                "action": "Pipeline completed successfully",
                "tool": "kaamkar_orchestrator",
                "reasoning": (
                    f"All {len(self.WORKFLOW_STAGES)} stages completed. "
                    f"Booking {booking['booking_id']} confirmed with {top_provider['name']}. "
                    f"3 follow-ups scheduled."
                ),
                "output": {
                    "booking_id": booking["booking_id"],
                    "stages_completed": len(self.WORKFLOW_STAGES),
                    "total_providers_evaluated": len(ranked_providers)
                }
            })

            return {
                "success": True,
                "session_id": session_id,
                "intent": intent,
                "location": location_info,
                "providers": ranked_providers[:5],  # Return top 5
                "booking": booking,
                "notifications": notifications,
                "followup": followup,
                "trace_log": trace_log,
                "workflow_stages": self.WORKFLOW_STAGES,
            }

        except Exception as e:
            logger.error(f"Orchestration error: {e}", exc_info=True)
            trace_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "Orchestrator",
                "action": "Pipeline error — graceful degradation",
                "tool": "error_handler",
                "reasoning": f"Error in pipeline: {str(e)}",
                "output": {"error": str(e)}
            })
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "trace_log": trace_log,
            }

    def _no_providers_response(self, intent, location_info, trace_log, session_id):
        """Handle case where no providers are found."""
        service = intent.get("service_type", "service")
        location = location_info.get("resolved_name", "your area")
        trace_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "Orchestrator",
            "action": "No providers found — pipeline terminated",
            "tool": "kaamkar_orchestrator",
            "reasoning": f"No {service} providers found near {location}.",
            "output": {"result": "no_providers"}
        })
        return {
            "success": False,
            "session_id": session_id,
            "error": f"No {service} providers found near {location}. Try a different area or service.",
            "intent": intent,
            "location": location_info,
            "providers": [],
            "trace_log": trace_log,
        }


# Singleton orchestrator instance
_orchestrator: Optional[KaamKarOrchestrator] = None


def get_orchestrator() -> KaamKarOrchestrator:
    """Get or create the singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = KaamKarOrchestrator()
    return _orchestrator
