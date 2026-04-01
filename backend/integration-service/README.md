# Integration Service

Layanan proxy yang menjembatani Orchestrator Service dengan Mock API. Bertindak sebagai unit verifikator tingkat pertama — meneruskan sinyal kegagalan eksplisit ke Orchestrator jika data tidak ditemukan.

## Setup

```bash
cd backend/integration-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

## Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/flights` | Forward ke Mock API `/flights` |
| GET | `/hotels` | Forward ke Mock API `/hotels` |
| GET | `/activities` | Forward ke Mock API `/activities` |
| GET | `/transport` | Forward ke Mock API `/transport` |

Parameter sama dengan Mock API. Lihat `docs/api-contracts/data-schemas.md`.

## Error Handling

| Status | Kondisi |
|---|---|
| 404 | Data tidak ditemukan di Mock API |
| 503 | Mock API tidak dapat dihubungi |