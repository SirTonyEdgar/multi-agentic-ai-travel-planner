# Orchestrator Service

Layanan inti yang mengelola seluruh logika kecerdasan buatan dalam sistem Multi-Agent AI Travel Planner. Mengimplementasikan pola ReAct (Reasoning and Acting) menggunakan LangChain dan Gemini AI.

## Setup

```bash
cd backend/orchestrator-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8001
```

File `.env` ada di root folder (sejajar docker-compose.yml)

## Endpoint

### `POST /plan-trip`

Menerima query dari API Gateway dan mengorkestrasi agen untuk menghasilkan rencana perjalanan.

**Request:**
```json
{
  "query": "Carikan tiket CGK ke Bali dan hotel budget 500 ribu",
  "session_id": null
}
```

**Response:**
```json
{
  "query": "...",
  "session_id": null,
  "response": "Berikut adalah rencana perjalanan Anda..."
}
```

## Tools yang Tersedia

| Tool | Deskripsi | Format Input |
|---|---|---|
| `cari_penerbangan` | Mencari tiket pesawat | `"ASAL,TUJUAN"` (contoh: `"CGK,DPS"`) |
| `cari_hotel` | Mencari hotel | `"LOKASI"` atau `"LOKASI,MAX_HARGA"` |
| `cari_aktivitas` | Mencari wisata/kuliner/ibadah | `"LOKASI"` atau `"LOKASI,KATEGORI"` |
| `cari_transport` | Mencari transport lokal | `"LOKASI"` atau `"LOKASI,JENIS"` |

## Arsitektur

- **LLM:** Model-agnostic via LangChain (default: Gemini 2.5 Flash)
- **Provider yang didukung:** Gemini, OpenAI, Anthropic, DeepSeek
- **Framework:** LangChain dengan pola Tool Calling (Single Agent) dan LangGraph (Multi-Agent)
- **Anti-halusinasi:** Semua data wajib bersumber dari Mock API (port 8002)
- **Max iterations:** 10 siklus penalaran per request