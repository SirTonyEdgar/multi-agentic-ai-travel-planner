# Multi-Agent AI Travel Planner

Backend orkestrasi Multi-Agent AI untuk aplikasi web perencana pariwisata. Sistem ini mentransformasi Large Language Model (LLM) dari sekadar antarmuka percakapan pasif menjadi agen otonom yang memitigasi halusinasi data lewat *grounding* ke sumber data eksternal, dengan arsitektur modular yang menjamin *fault isolation* antar domain.

Proyek ini adalah backend dari Tugas Akhir S1 Rekayasa Perangkat Lunak, Fakultas Informatika, Universitas Telkom.

**Demo langsung:** _(isi setelah deploy — lihat [DEPLOY.md](./DEPLOY.md))_

## Hasil Utama

Diuji pada 30 skenario formal (mencakup kasus lengkap, parsial, dan edge case):

| Arsitektur / Model | Akurasi Faktual | Hallucination Rate |
|---|---|---|
| Single Orchestrator Agent | 100% | 0% |
| Multi-Agent (LangGraph) | 100% | 0% |
| Gemini / ChatGPT standalone | 83,3% | 16,7% |

Pengujian *fault injection* (menghapus satu field data secara sengaja) menunjukkan arsitektur Multi-Agent tetap menghasilkan itinerary lengkap ketika satu domain gagal (*graceful degradation*), sementara Single-Agent gagal total.

## Arsitektur

```
Pengguna (browser)
      │
 API Gateway (:8080)  — satu-satunya pintu masuk publik
      │
 Orchestrator Service (:8001)
      │  4 agen spesialis (penerbangan/hotel/aktivitas/transportasi)
      │  + 1 Supervisor Agent, dibangun dengan LangChain + LangGraph
      ├──► ChromaDB (:8003)          — memori percakapan
      └──► Integration Service (:8000)
                │
                └──► Mock API (:8002) — ground truth data pariwisata
```

Lima layanan berjalan independen dalam container terpisah (Docker Compose). Setiap agen spesialis hanya bisa mengakses satu *tool* sesuai domainnya dan **wajib** mengambil data lewat *tool calling*, dilarang mengarang informasi — inilah mekanisme utama mitigasi halusinasi. Detail lengkap arsitektur dan hasil evaluasi ada di [`docs/api-contracts`](./docs/api-contracts).

## Tech Stack

- **Backend:** Python, FastAPI, LangChain, LangGraph, ChromaDB
- **LLM:** Model-agnostic — default Gemini, bisa diganti ke OpenAI/Anthropic/DeepSeek lewat env var
- **Frontend:** React + Vite (`frontend-jalan` untuk perencanaan trip, `frontend-pesan` untuk pemesanan hotel)
- **Infrastruktur:** Docker, Docker Compose

## Menjalankan secara lokal

1. Clone repo ini, lalu salin `.env.example` menjadi `.env` dan isi `GOOGLE_API_KEY` (gratis dari [Google AI Studio](https://aistudio.google.com/apikey)).
2. Jalankan:
   ```bash
   docker compose up --build
   ```
3. Buka:
   - Perencana trip: http://localhost:5173
   - Pemesanan hotel: http://localhost:5174
   - API Gateway: http://localhost:8080
   - Dokumentasi API tiap service: `http://localhost:<port>/docs` (Swagger, otomatis dari FastAPI)

## Deploy gratis ke Render

Lihat panduan langkah demi langkah di [DEPLOY.md](./DEPLOY.md). Repo ini sudah menyertakan `render.yaml` (Render Blueprint) yang mendefinisikan ketujuh service sekaligus.

## Batasan

Sesuai cakupan Tugas Akhir: backend memakai data simulasi (Mock API), bukan API komersial pihak ketiga; tidak ada eksekusi pemesanan/pembayaran nyata; cakupan destinasi terbatas pada tiga kota (Bali, Lombok, Yogyakarta).
