from fastapi import FastAPI, Query
from typing import List, Optional

# Inisialisasi aplikasi
app = FastAPI(title="Integration Service (Mock API)")

# ==========================================
# DATA DUMMY (MOCK DATA)
# ==========================================

# Data Hotel (Sesuai skema di docs/api-contracts)
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

# Data Penerbangan (Sesuai skema di docs/api-contracts)
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

# ==========================================
# ENDPOINTS (PINTU MASUK API)
# ==========================================

@app.get("/")
def read_root():
    return {
        "service": "Integration Service",
        "status": "active",
        "endpoints": ["/hotels", "/flights"]
    }

@app.get("/hotels")
def get_hotels():
    """Mengembalikan daftar semua hotel"""
    return MOCK_HOTELS

@app.get("/flights")
def get_flights():
    """Mengembalikan daftar semua penerbangan"""
    return MOCK_FLIGHTS

@app.get("/hotels")
def get_hotels(location: Optional[str] = None):
    """
    Mengambil data hotel. 
    Bisa difilter pakai ?location=Bali
    """
    if location:
        # Filter data: Ambil hotel yang lokasinya cocok (case insensitive)
        filtered_hotels = [
            h for h in MOCK_HOTELS 
            if h["location"].lower() == location.lower()
        ]
        return filtered_hotels
    return MOCK_HOTELS

@app.get("/flights")
def get_flights(destination: Optional[str] = None, origin: Optional[str] = None):
    """
    Mengambil data penerbangan.
    Bisa difilter pakai ?destination=DPS atau ?origin=CGK
    """
    results = MOCK_FLIGHTS
    
    if destination:
        results = [f for f in results if f["destination"].lower() == destination.lower()]
    
    if origin:
        results = [f for f in results if f["origin"].lower() == origin.lower()]
        
    return results