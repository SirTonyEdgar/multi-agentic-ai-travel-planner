# Mock API — Travel Planner Ground Truth

Layanan simulasi data pariwisata yang berfungsi sebagai **sumber kebenaran (ground truth)** untuk sistem Multi-Agent AI Travel Planner, sekaligus sebagai backend data untuk clone Traveloka pada frontend service.

---

## Setup

```bash
cd backend/mock-api
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn
uvicorn main:app --port 8002
```

Server berjalan di: `http://127.0.0.1:8002`

Swagger docs: `http://127.0.0.1:8002/docs`

---

## Endpoints

### `GET /flights`

| Parameter | Tipe | Wajib | Contoh |
|---|---|---|---|
| `origin` | string | ✓ | `CGK` |
| `destination` | string | ✓ | `DPS` |

```
GET /flights?origin=CGK&destination=DPS
```

### `GET /hotels`

| Parameter | Tipe | Wajib | Contoh |
|---|---|---|---|
| `location` | string | ✓ | `Bali` |
| `max_price` | integer | ✗ | `500000` |

```
GET /hotels?location=Bali
GET /hotels?location=Bali&max_price=500000
```

### `GET /activities`

| Parameter | Tipe | Wajib | Contoh |
|---|---|---|---|
| `location` | string | ✓ | `Bali` |
| `category` | string | ✗ | `wisata` / `kuliner` / `ibadah` |

```
GET /activities?location=Bali
GET /activities?location=Bali&category=wisata
```

---

## Data yang Tersedia

| Lokasi | Penerbangan | Hotel | Aktivitas |
|---|---|---|---|
| Bali (DPS) | CGK→DPS, SUB→DPS | 6 hotel | 8 aktivitas |
| Lombok (LOP) | CGK→LOP | 2 hotel | 2 aktivitas |
| Yogyakarta | - | 2 hotel | 4 aktivitas |

---

## Untuk Frontend Developer (Nizar)

Clone repo dan jalankan Mock API secara lokal:

```bash
git clone https://github.com/SirTonyEdgar/multi-agentic-ai-travel-planner
cd multi-agentic-ai-travel-planner/backend/mock-api
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn
uvicorn main:app --port 8002
```

Setiap kali ada update data dari backend, jalankan:

```bash
git pull
```

Server tidak perlu di-restart jika menggunakan `--reload`. Jika tidak, restart manual setelah `git pull`.

Untuk development dengan `--reload`:

```bash
uvicorn main:app --reload --port 8002
```

---

## Error Response

Jika data tidak ditemukan, endpoint mengembalikan HTTP 404:

```json
{
  "detail": "Tidak ada penerbangan tersedia untuk rute XXX -> YYY. Sistem tidak diperbolehkan menebak atau mengarang data."
}
```
