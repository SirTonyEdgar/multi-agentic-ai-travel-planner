import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from tools import cari_hotel, cari_penerbangan, cari_aktivitas

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI(title="Orchestrator Service")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

tools = [cari_penerbangan, cari_hotel, cari_aktivitas]

prompt = hub.pull("hwchase17/react")

prompt.template = """
Kamu adalah Agen Perjalanan Wisata profesional yang membantu pengguna merencanakan perjalanan.

INSTRUKSI WAJIB:
1. Jawab SELALU dalam Bahasa Indonesia.
2. Kamu memiliki akses ke alat berikut untuk mencari data NYATA:
{tools}

3. ATURAN KRITIS — ANTI HALUSINASI:
   - DILARANG KERAS mengarang harga, nama hotel, maskapai, atau informasi apapun.
   - Semua data WAJIB berasal dari hasil alat di atas.
   - Jika alat mengembalikan "DATA TIDAK DITEMUKAN", sampaikan jujur kepada user bahwa data tidak tersedia.
   - Jangan pernah mengasumsikan atau mengisi data yang tidak ada dari alat.

4. ATURAN PENGGUNAAN ALAT:
   - `cari_penerbangan`: Input format "ASAL,TUJUAN" (contoh: "CGK,DPS")
   - `cari_hotel`: Input nama kota (contoh: "Bali") atau "Kota,MaxHarga" (contoh: "Bali,500000")
   - `cari_aktivitas`: Input nama kota (contoh: "Bali") atau "Kota,kategori" (contoh: "Bali,wisata")

5. FORMAT BERPIKIR (ReAct):
Question: pertanyaan dari user
Thought: pikirkan apa yang perlu dicari dan alat mana yang digunakan
Action: pilih salah satu dari [{tool_names}]
Action Input: input untuk alat
Observation: hasil dari alat
... (ulangi Thought/Action/Observation sesuai kebutuhan)
Thought: Saya sudah punya semua data yang diperlukan
Final Answer: jawaban lengkap dan terstruktur berisi: Penerbangan (maskapai, jam, harga), Hotel (nama, harga/malam, fasilitas), Aktivitas (nama, harga tiket, jam buka). Tutup dengan total estimasi biaya.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=8
)


class TripRequest(BaseModel):
    query: str
    session_id: str | None = None


@app.get("/")
def read_root():
    return {"status": "Orchestrator Service Ready", "tools": ["cari_penerbangan", "cari_hotel", "cari_aktivitas"]}


@app.post("/plan-trip")
async def plan_trip(request: TripRequest):
    try:
        print(f"\n{'='*50}")
        print(f"[ORCHESTRATOR] Query: {request.query}")
        print(f"{'='*50}")

        # Jalankan di thread pool agar tidak block event loop FastAPI
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: agent_executor.invoke({"input": request.query})
        )

        response = result.get("output", "")
        print(f"[ORCHESTRATOR] Response: {response[:100]}...")

        return {
            "query": request.query,
            "session_id": request.session_id,
            "response": response
        }

    except Exception as e:
        print(f"[ORCHESTRATOR] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))