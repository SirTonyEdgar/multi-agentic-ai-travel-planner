# API Gateway

Pintu masuk tunggal untuk seluruh request dari frontend. Meneruskan query pengguna ke Orchestrator Service dan mengembalikan respons AI.

## Setup

```bash
cd backend/api-gateway
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8080
```

## Endpoint

### `GET /api/chat`

| Parameter | Tipe | Wajib | Contoh |
|---|---|---|---|
| `query` | string | ✓ | `Carikan tiket CGK ke Bali` |
| `session_id` | string | ✗ | `abc123` |

**Contoh request:**
```
GET /api/chat?query=Carikan tiket CGK ke Bali dan hotel budget 500 ribu
```

**Contoh response:**
```json
{
  "query": "Carikan tiket CGK ke Bali dan hotel budget 500 ribu",
  "session_id": null,
  "response": "Berikut adalah rencana perjalanan Anda..."
}
```

## Error Response

| Status | Kondisi |
|---|---|
| 503 | Orchestrator Service tidak dapat dihubungi |
| 500 | Orchestrator error (LLM atau tools gagal) |

## Catatan

- Endpoint `/api/chat` menggunakan Single Agent mode secara default.
- Untuk mengakses Multi-Agent mode, gunakan langsung ke Orchestrator Service:
    POST http://localhost:8001/plan-trip-multi