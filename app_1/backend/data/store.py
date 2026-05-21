"""
In-memory booking store (simulates Firebase/Supabase).
In production, replace with actual Firebase Admin SDK calls.
"""
import uuid
from datetime import datetime
from typing import Dict, Any

# In-memory stores
bookings: Dict[str, Any] = {}
notifications: Dict[str, list] = {}
followups: Dict[str, Any] = {}


def create_booking(provider: dict, intent: dict, slot: str) -> dict:
    """Simulate creating a booking and storing it."""
    booking_id = f"KK-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

    booking = {
        "booking_id": booking_id,
        "status": "confirmed",
        "provider": {
            "id": provider["id"],
            "name": provider["name"],
            "category": provider["category"],
            "phone": provider["phone"],
            "rating": provider["rating"],
        },
        "service": intent.get("service_type", provider["category"]),
        "location": intent.get("location", provider["area"]),
        "slot": slot,
        "urgency": intent.get("urgency", "normal"),
        "estimated_cost": f"PKR {provider['hourly_rate']} - {provider['hourly_rate'] * 2}",
        "eta_minutes": provider["response_time_min"],
        "created_at": now,
        "customer_language": intent.get("language", "english"),
        "notes": intent.get("raw_text", ""),
    }

    bookings[booking_id] = booking
    return booking


def get_booking(booking_id: str) -> dict:
    return bookings.get(booking_id, {})


def list_bookings() -> list:
    return list(bookings.values())


def update_booking_status(booking_id: str, status: str) -> bool:
    if booking_id in bookings:
        bookings[booking_id]["status"] = status
        bookings[booking_id]["updated_at"] = datetime.utcnow().isoformat()
        return True
    return False


def add_notification(booking_id: str, notification: dict):
    if booking_id not in notifications:
        notifications[booking_id] = []
    notifications[booking_id].append(notification)


def get_notifications(booking_id: str) -> list:
    return notifications.get(booking_id, [])
