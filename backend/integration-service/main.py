from typing import List, Optional
from fastapi import FastAPI, Query

app = FastAPI(title="Integration Service (Mock API)")

# TODO: Migrasi data statis ini ke dalam Database terpisah sesuai dengan desain arsitektur (Sub-bab 3.2.4).
# Penggunaan mock data ini bersifat sementara untuk menjamin validasi "Eksperimen Anti-Halusinasi" pada tahap pengujian.
MOCK_HOTELS = [
    {
        "hotel_id": "HTL-001",
        "name": "Kuta Beach Hotel",
        "location": "Bali",
        "rating": 4.5,
        "price_per_night": 750000,
        "amenities": ["WiFi", "Breakfast", "Pool"],
        "available_rooms": 3
    },
    {
        "hotel_id": "HTL-002",
        "name": "Ubud Zen Resort",
        "location": "Bali",
        "rating": 5.0,
        "price_per_night": 2500000,
        "amenities": ["WiFi", "Spa", "Yoga", "Pool"],
        "available_rooms": 1
    }
]

MOCK_FLIGHTS = [
    {
        "flight_id": "GA-402",
        "airline": "Garuda Indonesia",
        "origin": "CGK",
        "destination": "DPS",
        "departure_time": "08:00",
        "arrival_time": "10:50",
        "price": 1500000,
        "seat_class": "Economy",
        "availability": 5
    },
    {
        "flight_id": "QZ-7510",
        "airline": "AirAsia",
        "origin": "CGK",
        "destination": "DPS",
        "departure_time": "14:00",
        "arrival_time": "16:50",
        "price": 850000,
        "seat_class": "Economy",
        "availability": 2
    }
]

@app.get("/")
def read_root():
    """Health check endpoint for the Integration Service."""
    return {
        "service": "Integration Service",
        "status": "active",
        "endpoints": ["/hotels", "/flights"]
    }

@app.get("/hotels")
def get_hotels(location: Optional[str] = None):
    """Retrieve hotel data, optionally filtered by location."""
    if location:
        return [
            h for h in MOCK_HOTELS 
            if h["location"].lower() == location.lower()
        ]
    return MOCK_HOTELS

@app.get("/flights")
def get_flights(destination: Optional[str] = None, origin: Optional[str] = None):
    """Retrieve flight data, optionally filtered by origin and destination."""
    results = MOCK_FLIGHTS
    
    if destination:
        results = [f for f in results if f["destination"].lower() == destination.lower()]
    
    if origin:
        results = [f for f in results if f["origin"].lower() == origin.lower()]
        
    return results