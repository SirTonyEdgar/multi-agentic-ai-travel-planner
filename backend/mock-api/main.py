from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(
    title="Mock API - Travel Planner Ground Truth",
    description="Layanan simulasi data pariwisata sebagai sumber kebenaran (ground truth) untuk sistem Multi-Agent AI.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helper: load JSON data ─────────────────────────────────────────────────
def load_data(filename: str):
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Health Check ───────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "status": "Mock API Ready",
        "message": "Sumber data ground truth untuk Travel Planner AI",
        "endpoints": ["/flights", "/hotels", "/activities"]
    }


# ── Flights ────────────────────────────────────────────────────────────────
@app.get("/flights")
def get_flights(
    origin: str = Query(..., description="Kode bandara asal, contoh: CGK"),
    destination: str = Query(..., description="Kode bandara tujuan, contoh: DPS")
):
    """
    Mencari penerbangan berdasarkan rute asal dan tujuan.
    Mengembalikan daftar penerbangan yang tersedia beserta harga dan jadwal.
    Jika tidak ditemukan, mengembalikan sinyal kegagalan eksplisit.
    """
    data = load_data("flights.json")
    origin = origin.strip().upper()
    destination = destination.strip().upper()

    results = [
        f for f in data["flights"]
        if f["origin"].upper() == origin and f["destination"].upper() == destination
    ]

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Tidak ada penerbangan tersedia untuk rute {origin} → {destination}. "
                   f"Sistem tidak diperbolehkan menebak atau mengarang data penerbangan."
        )

    return {
        "route": f"{origin} → {destination}",
        "total_results": len(results),
        "flights": results
    }


# ── Hotels ─────────────────────────────────────────────────────────────────
@app.get("/hotels")
def get_hotels(
    location: str = Query(..., description="Nama kota atau lokasi, contoh: Bali"),
    max_price: int = Query(None, description="Filter harga maksimal per malam (opsional)")
):
    """
    Mencari hotel berdasarkan lokasi.
    Mendukung filter harga maksimal per malam.
    Jika tidak ditemukan, mengembalikan sinyal kegagalan eksplisit.
    """
    data = load_data("hotels.json")
    location_clean = location.strip().lower()

    results = [
        h for h in data["hotels"]
        if location_clean in h["location"].lower()
    ]

    if max_price:
        results = [h for h in results if h["price_per_night"] <= max_price]

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Tidak ada hotel tersedia di lokasi '{location}'. "
                   f"Sistem tidak diperbolehkan menebak atau mengarang data hotel."
        )

    return {
        "location": location,
        "total_results": len(results),
        "hotels": sorted(results, key=lambda x: x["price_per_night"])
    }


# ── Activities ─────────────────────────────────────────────────────────────
@app.get("/activities")
def get_activities(
    location: str = Query(..., description="Nama kota atau lokasi, contoh: Bali"),
    category: str = Query(None, description="Kategori aktivitas: wisata, kuliner, ibadah (opsional)")
):
    """
    Mencari aktivitas dan tempat wisata berdasarkan lokasi.
    Mendukung filter berdasarkan kategori.
    Jika tidak ditemukan, mengembalikan sinyal kegagalan eksplisit.
    """
    data = load_data("activities.json")
    location_clean = location.strip().lower()

    results = [
        a for a in data["activities"]
        if location_clean in a["location"].lower()
    ]

    if category:
        results = [a for a in results if a["category"].lower() == category.strip().lower()]

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Tidak ada aktivitas tersedia di lokasi '{location}'. "
                   f"Sistem tidak diperbolehkan menebak atau mengarang data aktivitas."
        )

    return {
        "location": location,
        "category_filter": category,
        "total_results": len(results),
        "activities": results
    }
