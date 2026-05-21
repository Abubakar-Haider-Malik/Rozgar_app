"""
FastAPI router for KaamKar AI core endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.core.orchestrator import get_orchestrator
from backend.data.store import get_booking, list_bookings, get_notifications
from backend.data.providers import PROVIDERS, CATEGORY_ALIASES

router = APIRouter()


# ── Request/Response Models ──

class ServiceRequest(BaseModel):
    text: str
    user_id: Optional[str] = "guest"


class BookingStatusRequest(BaseModel):
    booking_id: str


# ── Demo scenarios ──
DEMO_SCENARIOS = [
    {
        "id": "demo1",
        "title": "AC Technician Request",
        "text": "Mujhe kal subah G-13 mein AC technician chahiye",
        "description": "Roman Urdu request for AC repair in G-13 tomorrow morning",
        "category": "AC Technician",
        "language": "roman_urdu"
    },
    {
        "id": "demo2",
        "title": "Emergency Plumber",
        "text": "Emergency! Urgent plumber chahiye abhi F-10 mein, paani leak ho raha hai!",
        "description": "Urgent mixed-language emergency plumber request",
        "category": "Plumber",
        "language": "roman_urdu"
    },
    {
        "id": "demo3",
        "title": "Female Beautician",
        "text": "Female beautician chahiye ghar pe, Bahria Town, kal dopahar ko",
        "description": "Request for female beautician at home in Bahria Town",
        "category": "Beautician",
        "language": "roman_urdu"
    },
    {
        "id": "demo4",
        "title": "Math Tutor Booking",
        "text": "I need a maths and physics tutor for O-Levels in DHA Phase 2",
        "description": "English request for O-Level tutor in DHA",
        "category": "Tutor",
        "language": "english"
    },
    {
        "id": "demo5",
        "title": "Urgent Electrician",
        "text": "Bijli chali gayi! Electrician chahiye foran I-8 mein",
        "description": "Urgent power outage — electrician needed immediately in I-8",
        "category": "Electrician",
        "language": "roman_urdu"
    },
]


# ── API Routes ──

@router.post("/request")
async def process_service_request(req: ServiceRequest):
    """
    Main endpoint: processes a natural language service request
    through the full multi-agent pipeline.
    """
    if not req.text or len(req.text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Request text is too short.")

    orchestrator = get_orchestrator()
    result = orchestrator.process_request(req.text.strip())
    return result


@router.get("/booking/{booking_id}")
async def get_booking_details(booking_id: str):
    """Retrieve booking details by ID."""
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found.")
    notifications = get_notifications(booking_id)
    return {"booking": booking, "notifications": notifications}


@router.get("/bookings")
async def list_all_bookings():
    """List all bookings (for demo/history view)."""
    return {"bookings": list_bookings()}


import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@router.get("/providers")
async def get_providers(
    category: Optional[str] = None, 
    sort_by: Optional[str] = "nearest", 
    lat: Optional[float] = 33.626,  # Default to NUTECH area if not provided
    lng: Optional[float] = 73.042
):
    """Get provider list with smart filters and distance sorting."""
    providers = []
    
    for p in PROVIDERS:
        # Calculate distance if we have lat/lng
        dist = haversine(lat, lng, p["lat"], p["lng"]) if lat and lng else 0
        
        # Clone dict to avoid mutating global data
        p_data = dict(p)
        p_data["distance_km"] = round(dist, 1)
        providers.append(p_data)
        
    if category and category.lower() != "all":
        providers = [p for p in providers if p["category"].lower() == category.lower()]
        
    # Smart sorting
    if sort_by == "nearest":
        providers.sort(key=lambda x: x["distance_km"])
    elif sort_by == "cheapest":
        providers.sort(key=lambda x: x["hourly_rate"])
    elif sort_by == "highest_rated":
        providers.sort(key=lambda x: x["rating"], reverse=True)
        
    return {"providers": providers, "total": len(providers)}


@router.get("/categories")
async def get_categories():
    """Get all available service categories."""
    cats = list(set(p["category"] for p in PROVIDERS))
    return {"categories": sorted(cats)}


@router.get("/demos")
async def get_demo_scenarios():
    """Get predefined demo scenarios."""
    return {"scenarios": DEMO_SCENARIOS}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "KaamKar AI", "version": "1.0.0"}
