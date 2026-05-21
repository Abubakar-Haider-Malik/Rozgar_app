"""
BookingAgent: Simulates slot reservation and booking confirmation.
NotificationAgent: Generates confirmation/reminder messages.
FollowUpAgent: Schedules reminders and completion checks.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from backend.data.store import create_booking, add_notification


class BookingAgent:
    """
    Agent 6: Simulates booking a slot with the top-ranked provider.
    Generates booking ID, receipt, and ETA.
    """

    def __init__(self):
        self.agent_name = "BookingAgent"

    def run(self, top_provider: dict, intent: dict, trace_log: list) -> dict:
        start = datetime.utcnow().isoformat()

        # Pick preferred slot based on time_preference
        available_slots = top_provider.get("available_slots", ["10:00 AM"])
        time_pref = intent.get("time_preference", "")
        selected_slot = self._pick_slot(available_slots, time_pref)

        # Create booking in store
        booking = create_booking(top_provider, intent, selected_slot)

        # Calculate ETA
        eta = datetime.utcnow() + timedelta(minutes=top_provider.get("response_time_min", 30))
        booking["eta_timestamp"] = eta.isoformat()

        trace_log.append({
            "timestamp": start,
            "agent": self.agent_name,
            "action": f"Created booking {booking['booking_id']} with {top_provider['name']}",
            "tool": "booking_database",
            "reasoning": (
                f"Selected slot '{selected_slot}' based on preference '{time_pref}'. "
                f"Provider {top_provider['name']} has ETA {top_provider['response_time_min']} min. "
                f"Booking confirmed with ID: {booking['booking_id']}"
            ),
            "output": {
                "booking_id": booking["booking_id"],
                "provider": top_provider["name"],
                "slot": selected_slot,
                "status": "confirmed",
                "eta_minutes": top_provider["response_time_min"],
                "estimated_cost": booking["estimated_cost"]
            }
        })

        return booking

    def _pick_slot(self, slots: list, time_pref: Optional[str]) -> str:
        """Pick the best available slot based on time preference."""
        if not slots:
            return "10:00 AM"

        pref_map = {
            "morning": ["8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM"],
            "afternoon": ["12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"],
            "evening": ["4:00 PM", "5:00 PM", "6:00 PM"],
            "night": ["7:00 PM", "8:00 PM", "9:00 PM"],
        }

        preferred = pref_map.get(time_pref, [])
        for preferred_time in preferred:
            if preferred_time in slots:
                return preferred_time

        return slots[0]  # Default to first available


class NotificationAgent:
    """
    Agent 7: Generates booking confirmations, reminders, and status updates.
    """

    def __init__(self):
        self.agent_name = "NotificationAgent"

    def run(self, booking: dict, intent: dict, trace_log: list) -> dict:
        start = datetime.utcnow().isoformat()
        language = intent.get("language", "english")

        # Generate messages in the user's language
        confirmation = self._gen_confirmation(booking, language)
        reminder = self._gen_reminder(booking, language)

        notifications = {
            "confirmation": confirmation,
            "reminder": reminder,
            "channel": "in_app",
        }

        # Store in notification DB
        add_notification(booking["booking_id"], {
            "type": "confirmation",
            "message": confirmation,
            "timestamp": start,
        })
        add_notification(booking["booking_id"], {
            "type": "reminder",
            "message": reminder,
            "timestamp": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        })

        trace_log.append({
            "timestamp": start,
            "agent": self.agent_name,
            "action": "Generated booking confirmation and reminder notifications",
            "tool": "notification_engine",
            "reasoning": (
                f"Detected user language: '{language}'. "
                f"Generated confirmation for booking {booking['booking_id']} "
                f"and scheduled reminder 1 hour before appointment."
            ),
            "output": {
                "confirmation_preview": confirmation[:100] + "...",
                "reminder_scheduled": True,
                "language": language
            }
        })

        return notifications

    def _gen_confirmation(self, booking: dict, language: str) -> str:
        bid = booking["booking_id"]
        provider = booking["provider"]["name"]
        slot = booking["slot"]
        cost = booking["estimated_cost"]
        eta = booking["eta_minutes"]

        if language in ("roman_urdu", "urdu"):
            return (
                f"✅ آپ کی بکنگ تصدیق ہو گئی!\n\n"
                f"🆔 Booking ID: {bid}\n"
                f"👤 Provider: {provider}\n"
                f"⏰ Slot: {slot}\n"
                f"💰 Takariban: {cost}\n"
                f"🚗 ETA: {eta} minute\n\n"
                f"Shukriya KaamKar AI use karne ka! 🙏"
            )
        return (
            f"✅ Booking Confirmed!\n\n"
            f"🆔 Booking ID: {bid}\n"
            f"👤 Provider: {provider}\n"
            f"⏰ Slot: {slot}\n"
            f"💰 Estimated Cost: {cost}\n"
            f"🚗 ETA: {eta} minutes\n\n"
            f"Thank you for using KaamKar AI! 🙏"
        )

    def _gen_reminder(self, booking: dict, language: str) -> str:
        provider = booking["provider"]["name"]
        slot = booking["slot"]
        if language in ("roman_urdu", "urdu"):
            return f"⏰ Yaad dahanai: Aapka {provider} ka {slot} wala appointment qareeb aa raha hai. Tayyar rahain!"
        return f"⏰ Reminder: Your appointment with {provider} at {slot} is coming up soon. Please be ready!"


class FollowUpAgent:
    """
    Agent 8: Schedules follow-up reminders, completion confirmation,
    and customer satisfaction checks.
    """

    def __init__(self):
        self.agent_name = "FollowUpAgent"

    def run(self, booking: dict, intent: dict, trace_log: list) -> dict:
        start = datetime.utcnow().isoformat()
        language = intent.get("language", "english")

        now = datetime.utcnow()
        followups = [
            {
                "type": "pre_appointment",
                "scheduled_at": (now + timedelta(hours=1)).isoformat(),
                "message": self._pre_appointment_msg(booking, language),
            },
            {
                "type": "completion_check",
                "scheduled_at": (now + timedelta(hours=4)).isoformat(),
                "message": self._completion_msg(booking, language),
            },
            {
                "type": "satisfaction_survey",
                "scheduled_at": (now + timedelta(hours=6)).isoformat(),
                "message": self._satisfaction_msg(booking, language),
            },
        ]

        trace_log.append({
            "timestamp": start,
            "agent": self.agent_name,
            "action": "Scheduled 3 follow-up interactions for booking lifecycle",
            "tool": "followup_scheduler",
            "reasoning": (
                f"Booking {booking['booking_id']} confirmed. "
                f"Scheduling: (1) pre-appointment reminder in 1hr, "
                f"(2) completion check in 4hrs, "
                f"(3) satisfaction survey in 6hrs. "
                f"Language: {language}"
            ),
            "output": {
                "followups_count": len(followups),
                "types": [f["type"] for f in followups],
                "booking_id": booking["booking_id"]
            }
        })

        return {"booking_id": booking["booking_id"], "followups": followups}

    def _pre_appointment_msg(self, booking: dict, lang: str) -> str:
        p = booking["provider"]["name"]
        s = booking["slot"]
        if lang in ("roman_urdu", "urdu"):
            return f"🔔 Aapka {p} {s} ko aa raha hai. Ghar kholi rakhein!"
        return f"🔔 {p} is on their way for your {s} appointment. Please be available!"

    def _completion_msg(self, booking: dict, lang: str) -> str:
        p = booking["provider"]["name"]
        if lang in ("roman_urdu", "urdu"):
            return f"✅ Kya {p} ki service complete ho gayi? Reply 'haan' ya 'nahi'."
        return f"✅ Has {p} completed the service? Reply 'yes' or 'no'."

    def _satisfaction_msg(self, booking: dict, lang: str) -> str:
        if lang in ("roman_urdu", "urdu"):
            return "⭐ Humein batain: aaj ki service kaisi rahi? 1-5 star rating dain!"
        return "⭐ How was your experience today? Please rate the service 1-5 stars!"
