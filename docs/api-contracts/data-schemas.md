# Skema Data Mock API (Sederhana)

Dokumen ini mendefinisikan struktur data JSON yang akan dikembalikan oleh Integration Service (Mock API).
Tujuannya agar Searcher Agent (AI) tahu field apa saja yang tersedia untuk dibaca.

## 1. Tiket Pesawat (Flight)
Endpoint target: `/flights`

Contoh respons JSON untuk satu penerbangan:
```json
{
  "flight_id": "GA-402",           // ID unik untuk booking
  "airline": "Garuda Indonesia",   // Nama maskapai
  "origin": "CGK",                 // Bandara asal (Kode IATA)
  "destination": "DPS",            // Bandara tujuan (Kode IATA)
  "departure_time": "08:00",       // Jam keberangkatan
  "arrival_time": "10:50",         // Jam tiba
  "price": 1500000,                // Harga dalam Rupiah (IDR)
  "seat_class": "Economy",         // Kelas kursi
  "availability": 5                // Sisa kursi (Penting untuk validasi AI)
}

{
  "hotel_id": "HTL-001",           // ID unik hotel
  "name": "Kuta Beach Hotel",      // Nama Hotel
  "location": "Bali",              // Kota/Area
  "rating": 4.5,                   // Bintang/Rating (Skala 1-5)
  "price_per_night": 750000,       // Harga per malam
  "amenities": [                   // Fasilitas utama (Array string)
    "WiFi",
    "Breakfast",
    "Pool"
  ],
  "available_rooms": 3             // Sisa kamar (Penting untuk validasi AI)
}