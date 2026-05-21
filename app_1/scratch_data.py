import json
import random

CATEGORIES = [
    "Laundry", "Carpenter", "Cobbler / Shoe Repair", "Window Fixer", "Computer Repair",
    "Laptop Repair", "Mobile Repair", "AC Technician", "Electrician", "Plumber",
    "Painter", "Cleaning", "Pest Control", "Water Tank Cleaning", "Movers",
    "Locksmith", "Gardening", "Interior Work", "Beauty Services", "Salon",
    "Doctor Visit", "Lab Test", "Bike Mechanic", "Car Mechanic"
]

AREAS = [
    {"area": "G-13", "lat": 33.6844, "lng": 73.0479},
    {"area": "F-10", "lat": 33.7077, "lng": 73.0252},
    {"area": "F-7", "lat": 33.7198, "lng": 73.0551},
    {"area": "I-8", "lat": 33.6938, "lng": 73.0551},
    {"area": "I-10", "lat": 33.6760, "lng": 73.0680},
    {"area": "Bahria Town", "lat": 33.5553, "lng": 73.1093},
    {"area": "DHA", "lat": 33.5189, "lng": 73.1032},
    {"area": "Rawalpindi", "lat": 33.5970, "lng": 73.0504},
    {"area": "NUTECH Surroundings", "lat": 33.6260, "lng": 73.0420},
    {"area": "G-11", "lat": 33.6823, "lng": 73.0135}
]

NAMES_FIRST = ["Ali", "Ahmed", "Bilal", "Usman", "Tariq", "Hassan", "Kareem", "Sajid", "Rafiq", "Aslam", "Zain", "Omar", "Imran", "Kamran", "Faisal"]
NAMES_LAST = ["Raza", "Khan", "Tech", "Services", "Masters", "Pro", "Fix", "Care", "Squad", "Express", "Works", "Solutions"]

PROVIDERS = []
pid = 1

for cat in CATEGORIES:
    for i in range(5):
        area_obj = random.choice(AREAS)
        
        # Add random jitter to lat/lng so they aren't directly on top of each other
        lat = area_obj["lat"] + random.uniform(-0.02, 0.02)
        lng = area_obj["lng"] + random.uniform(-0.02, 0.02)
        
        # Generate realistic rating, jobs, price
        rating = round(random.uniform(3.8, 5.0), 1)
        jobs = random.randint(10, 1000)
        
        # Prices depend slightly on category, but random for now
        base_price = random.randint(500, 3000)
        base_price = int(base_price / 100) * 100  # round to nearest 100
        
        name = f"{random.choice(NAMES_FIRST)} {random.choice(NAMES_LAST)}"
        if i == 0 and "AC" in cat: name = "Ali Raza (Premium)"
        
        provider = {
            "id": f"p{pid:03d}",
            "name": name,
            "category": cat,
            "area": area_obj["area"],
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "rating": rating,
            "available_slots": ["10:00 AM", "2:00 PM"],
            "response_time_min": random.choice([15, 30, 45, 60, 90, 120]),
            "hourly_rate": base_price,
            "phone": f"+92-300-{random.randint(1000000, 9999999)}",
            "jobs_done": jobs,
            "verified": random.choice([True, True, False]),
            "avatar": f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=random&color=fff",
            "description": f"Expert {cat} with {random.randint(2, 10)} years of experience in {area_obj['area']}."
        }
        PROVIDERS.append(provider)
        pid += 1

with open("d:/app_1/backend/data/providers.py", "w", encoding="utf-8") as f:
    f.write('"""\nMock provider database for KaamKar AI.\n120 providers across Islamabad/Rawalpindi in 24 categories.\n"""\n\n')
    f.write('PROVIDERS = [\n')
    for p in PROVIDERS:
        f.write(f'    {json.dumps(p)},\n')
    f.write(']\n\n')
    f.write('CATEGORY_ALIASES = {}\n') # keep empty or add basic if needed
