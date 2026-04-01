# Mock API — Travel Planner Ground Truth

Layanan simulasi data pariwisata yang berfungsi sebagai **sumber kebenaran (ground truth)** untuk sistem Multi-Agent AI Travel Planner, sekaligus sebagai backend data untuk frontend clone Traveloka.

---

## Setup

```bash
cd backend/mock-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8002
```

Server: `http://127.0.0.1:8002` | Docs: `http://127.0.0.1:8002/docs`

---

## Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/flights` | Cari penerbangan berdasarkan rute |
| GET | `/hotels` | Cari hotel berdasarkan lokasi |
| GET | `/activities` | Cari aktivitas wisata/kuliner/ibadah |
| GET | `/transport` | Cari transportasi lokal |

Lihat `docs/api-contracts/data-schemas.md` untuk detail lengkap schema response.

---

## Data yang Tersedia

| Lokasi | Penerbangan | Hotel | Aktivitas | Transport |
|---|---|---|---|---|
| Bali (DPS) | CGK→DPS, SUB→DPS | 6 hotel | 8 aktivitas | 6 opsi |
| Lombok (LOP) | CGK→LOP | 2 hotel | 2 aktivitas | 3 opsi |
| Yogyakarta | - | 2 hotel | 4 aktivitas | 3 opsi |

---

## Untuk Frontend Developer (Nizar)

```bash
git clone https://github.com/SirTonyEdgar/multi-agentic-ai-travel-planner
cd multi-agentic-ai-travel-planner/backend/mock-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

Setiap kali ada update data: `git pull` (tidak perlu install ulang).

---

## Error Response

Jika data tidak ditemukan → HTTP 404:

```json
{
  "detail": "Tidak ada [data] tersedia di lokasi '[lokasi]'. Sistem tidak diperbolehkan menebak atau mengarang data."
}
```