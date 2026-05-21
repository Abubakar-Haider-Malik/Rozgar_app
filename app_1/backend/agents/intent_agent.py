"""
IntentAgent: Detects language, parses Urdu/Roman Urdu/English,
extracts service type, urgency, location, and time/date.
Uses Gemini API for NLP reasoning.
"""
import re
import os
import json
from datetime import datetime
from typing import Optional

import google.generativeai as genai

from backend.data.providers import CATEGORY_ALIASES, LOCATION_MAP


# Roman Urdu / Urdu keyword maps for fast local matching
URGENCY_KEYWORDS = {
    "emergency": "urgent", "urgent": "urgent", "abhi": "urgent",
    "jaldi": "urgent", "foran": "urgent", "turant": "urgent",
    "zaruri": "urgent", "emergency hai": "urgent",
    "kal": "tomorrow", "parso": "day_after_tomorrow",
    "subah": "morning", "shaam": "evening", "raat": "night",
    "aaj": "today", "today": "today", "tomorrow": "tomorrow",
}

TIME_KEYWORDS = {
    "subah": "morning", "morning": "morning",
    "dopahar": "afternoon", "afternoon": "afternoon",
    "shaam": "evening", "evening": "evening",
    "raat": "night", "night": "night",
    "10 baje": "10:00 AM", "10 bajay": "10:00 AM",
}


def detect_language(text: str) -> str:
    """Heuristic language detection: Urdu script, Roman Urdu, or English."""
    urdu_pattern = re.compile(r'[\u0600-\u06FF]')
    if urdu_pattern.search(text):
        return "urdu"

    roman_urdu_words = ["mujhe", "chahiye", "karo", "hai", "kal", "subah",
                        "abhi", "jaldi", "wala", "walay", "bhi", "koi", "yahan",
                        "ghar", "mein", "ka", "ki", "ko", "se", "par", "aur"]
    words = text.lower().split()
    roman_hits = sum(1 for w in words if w in roman_urdu_words)
    if roman_hits >= 2:
        return "roman_urdu"

    return "english"


def extract_location_heuristic(text: str) -> Optional[str]:
    """Try to find known location keywords in the text."""
    text_lower = text.lower()
    # Sort by length desc to match longer names first
    for key in sorted(LOCATION_MAP.keys(), key=len, reverse=True):
        if key in text_lower:
            return LOCATION_MAP[key]["full_name"]
    # Pattern: G-\d+, F-\d+, I-\d+, H-\d+, E-\d+
    sector = re.search(r'\b([A-HI]-\d{1,2})\b', text, re.IGNORECASE)
    if sector:
        return sector.group(1).upper()
    return None


def extract_category_heuristic(text: str) -> Optional[str]:
    """Try to match service category from text."""
    text_lower = text.lower()
    for alias, category in sorted(CATEGORY_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
        if alias in text_lower:
            return category
    return None


class IntentAgent:
    """
    Agent 1: Intent & Entity Extraction.
    Uses Gemini API for NLP + local heuristics as fallback.
    """

    def __init__(self, gemini_model=None):
        self.model = gemini_model
        self.agent_name = "IntentAgent"

    def run(self, user_text: str, trace_log: list) -> dict:
        """
        Main entry point.
        Returns structured intent dict + appends to trace_log.
        """
        start = datetime.utcnow().isoformat()
        language = detect_language(user_text)

        # Try Gemini first, fallback to heuristics
        result = None
        tool_used = "local_heuristics"

        if self.model:
            try:
                result = self._extract_with_gemini(user_text, language)
                tool_used = "gemini_api"
            except Exception as e:
                result = None

        if not result:
            result = self._extract_heuristic(user_text, language)

        result["language"] = language
        result["raw_text"] = user_text
        result["confidence"] = result.get("confidence", 0.85)

        trace_log.append({
            "timestamp": start,
            "agent": self.agent_name,
            "action": "Extracted intent and entities from user request",
            "tool": tool_used,
            "reasoning": f"Detected language: {language}. Parsed service type, location, urgency from: '{user_text[:80]}'",
            "output": result
        })

        return result

    def _extract_with_gemini(self, text: str, language: str) -> dict:
        """Use Gemini to extract structured intent from multilingual text."""
        prompt = f"""
You are an AI assistant for a Pakistani service booking app. Extract structured information from this service request.

User request: "{text}"
Detected language: {language}

Extract the following fields as JSON:
- service_type: The type of service requested (AC Technician, Plumber, Electrician, Beautician, Tutor, Cleaner, Mechanic, Carpenter, Painter, Laundry, Gardener, Tailor, Car Washer)
- location: The area/location mentioned (e.g., G-13, F-10, Bahria Town, or null if not mentioned)
- urgency: "urgent", "tomorrow", "today", "scheduled", or "flexible"
- time_preference: morning, afternoon, evening, night, or specific time like "10:00 AM"
- date_preference: today, tomorrow, day_after_tomorrow, or specific date
- special_notes: any special requirements (e.g., female only, specific brand)
- confidence: 0.0-1.0 confidence score

Reply ONLY with valid JSON. No explanation.
"""
        response = self.model.generate_content(prompt)
        text_resp = response.text.strip()
        # Strip markdown code fences if present
        text_resp = re.sub(r'^```(?:json)?\s*', '', text_resp)
        text_resp = re.sub(r'\s*```$', '', text_resp)
        return json.loads(text_resp)

    def _extract_heuristic(self, text: str, language: str) -> dict:
        """Fallback rule-based extraction."""
        service_type = extract_category_heuristic(text) or "General Service"
        location = extract_location_heuristic(text)

        # Urgency detection
        urgency = "flexible"
        text_lower = text.lower()
        if any(k in text_lower for k in ["abhi", "jaldi", "foran", "emergency", "urgent", "turant"]):
            urgency = "urgent"
        elif any(k in text_lower for k in ["kal", "tomorrow"]):
            urgency = "tomorrow"
        elif any(k in text_lower for k in ["aaj", "today"]):
            urgency = "today"

        # Time preference
        time_pref = None
        if any(k in text_lower for k in ["subah", "morning"]):
            time_pref = "morning"
        elif any(k in text_lower for k in ["shaam", "evening"]):
            time_pref = "evening"
        elif any(k in text_lower for k in ["dopahar", "afternoon"]):
            time_pref = "afternoon"

        return {
            "service_type": service_type,
            "location": location,
            "urgency": urgency,
            "time_preference": time_pref,
            "date_preference": urgency if urgency in ["today", "tomorrow"] else "flexible",
            "special_notes": None,
            "confidence": 0.70,
        }
