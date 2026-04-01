# API Contract — Mock API Data Schemas

Dokumen ini mendefinisikan struktur data JSON yang dikembalikan oleh setiap endpoint Mock API.
Digunakan sebagai referensi oleh Orchestrator Agent dan Frontend Developer.

---

## Endpoint: `GET /flights`

**Query Parameters:**
| Parameter | Tipe | Wajib |
|---|---|---|
| `origin` | string (IATA) | ✓ |
| `destination` | string (IATA) | ✓ |

**Response:**
```json
{
  "route": "CGK → DPS",
  "total_results": 5,
  "flights": [
    {
      "id": "FL001",
      "airline": "Garuda Indonesia",
      "flight_number": "GA-406",
      "origin": "CGK",
      "destination": "DPS",
      "departure": "06:00",
      "arrival": "08:55",
      "duration_minutes": 115,
      "price": 850000,
      "class": "Economy",
      "seats_available": 12
    }
  ]
}
```

**Kode Bandara yang Tersedia:**
| Kode | Bandara |
|---|---|
| CGK | Soekarno-Hatta, Jakarta |
| SUB | Juanda, Surabaya |
| DPS | Ngurah Rai, Bali |
| LOP | Praya, Lombok |

---

## Endpoint: `GET /hotels`

**Query Parameters:**
| Parameter | Tipe | Wajib |
|---|---|---|
| `location` | string | ✓ |
| `max_price` | integer | ✗ |

**Response:**
```json
{
  "location": "Bali",
  "total_results": 6,
  "hotels": [
    {
      "id": "HT001",
      "name": "The Layar Private Villas",
      "location": "Bali",
      "area": "Seminyak",
      "rating": 4.8,
      "price_per_night": 1200000,
      "room_type": "Villa",
      "facilities": ["kolam renang", "sarapan", "wifi", "AC", "parkir"],
      "rooms_available": 3,
      "address": "Jl. Laksmana No.68, Seminyak, Bali"
    }
  ]
}
```

---

## Endpoint: `GET /activities`

**Query Parameters:**
| Parameter | Tipe | Wajib | Nilai |
|---|---|---|---|
| `location` | string | ✓ | |
| `category` | string | ✗ | `wisata` / `kuliner` / `ibadah` |

**Response:**
```json
{
  "location": "Bali",
  "category_filter": "wisata",
  "total_results": 5,
  "activities": [
    {
      "id": "AC001",
      "name": "Tanah Lot",
      "location": "Bali",
      "area": "Tabanan",
      "category": "wisata",
      "description": "Pura di atas batu karang di tepi laut.",
      "entry_fee": 60000,
      "open_hours": "07:00 - 19:00",
      "duration_recommended_hours": 2,
      "rating": 4.7
    }
  ]
}
```

---

## Endpoint: `GET /transport`

**Query Parameters:**
| Parameter | Tipe | Wajib | Nilai |
|---|---|---|---|
| `location` | string | ✓ | |
| `type` | string | ✗ | `Shuttle Bandara` / `Rental Mobil` / `Rental Motor` / `Taksi` |

**Response:**
```json
{
  "location": "Bali",
  "type_filter": null,
  "total_results": 6,
  "transports": [
    {
      "id": "TR001",
      "type": "Shuttle Bandara",
      "provider": "Kura-Kura Bus",
      "location": "Bali",
      "origin": "Bandara Ngurah Rai (DPS)",
      "destination": "Kuta",
      "price": 60000,
      "duration_minutes": 30,
      "schedule": "Setiap 30 menit",
      "open_hours": "06:00 - 23:00",
      "seats_available": 20
    }
  ]
}
```

---

## Error Response (404)

Jika data tidak ditemukan, semua endpoint mengembalikan HTTP 404:

```json
{
  "detail": "Tidak ada [data] tersedia di lokasi '[lokasi]'. Sistem tidak diperbolehkan menebak atau mengarang data."
}
```

Orchestrator Agent **wajib menghentikan pencarian** dan memberikan fallback response kepada user jika menerima 404.

---

## Data yang Tersedia

| Lokasi | Penerbangan | Hotel | Aktivitas | Transport |
|---|---|---|---|---|
| Bali (DPS) | CGK→DPS, SUB→DPS | 6 hotel | 8 aktivitas | 6 opsi |
| Lombok (LOP) | CGK→LOP | 2 hotel | 2 aktivitas | 3 opsi |
| Yogyakarta | - | 2 hotel | 4 aktivitas | 3 opsi |
