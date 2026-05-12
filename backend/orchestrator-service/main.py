import os
import asyncio
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Optional
from tools import cari_hotel, cari_penerbangan, cari_aktivitas, cari_transport
from memory import save_conversation, get_relevant_context

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI(title="Orchestrator Service")

# ============================================================
# LLM
# ============================================================
def get_llm():
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model = os.getenv("LLM_MODEL", "gemini-2.5-flash")

    if provider == "openai":
        return ChatOpenAI(model=model or "gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    elif provider == "anthropic":
        return ChatAnthropic(model=model or "claude-3-5-sonnet-20241022", temperature=0, api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif provider == "deepseek":
        return ChatOpenAI(model=model or "deepseek-chat", temperature=0, api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")
    else:  # default: gemini
        return ChatGoogleGenerativeAI(model=model, temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"))

llm = get_llm()

# ============================================================
# SINGLE AGENT SETUP
# ============================================================
tools = [cari_penerbangan, cari_hotel, cari_aktivitas, cari_transport]

single_prompt = ChatPromptTemplate.from_messages([
    ("system", """Kamu adalah Agen Perjalanan Wisata Indonesia yang membantu pengguna merencanakan perjalanan.

INSTRUKSI WAJIB:
1. Jawab SELALU dalam Bahasa Indonesia.
2. Gunakan tools yang tersedia untuk mencari data NYATA. DILARANG mengarang informasi.
3. Jika tool mengembalikan DATA TIDAK DITEMUKAN, sampaikan jujur ke user.

ATURAN PENGGUNAAN TOOLS:

- cari_penerbangan: format "ASAL,TUJUAN" menggunakan kode IATA.
  Kode bandara yang tersedia: CGK (Jakarta), SUB (Surabaya), DPS (Bali), LOP (Lombok)
  Jika kota asal/tujuan ada di daftar → gunakan kodenya dan panggil tool.
  Jika kota asal/tujuan TIDAK ada di daftar → JANGAN panggil tool, sampaikan rute tidak tersedia.
  Jika kota asal tidak disebutkan → JANGAN panggil tool, minta klarifikasi ke user.
  Tetap lanjutkan mencari layanan lain meskipun penerbangan tidak bisa dicari.

- cari_hotel: "KOTA" atau "KOTA,MAX_HARGA"
  Kota yang tersedia: Bali, Lombok, Yogyakarta
  Area spesifik (Ubud, Kuta, Senggigi, dll) → tetap gunakan nama kota utama.
  Jika lokasi tidak ada dalam daftar → JANGAN panggil tool, sampaikan data tidak tersedia.

- cari_aktivitas: "KOTA" atau "KOTA,KATEGORI"
  Kota yang tersedia: Bali, Lombok, Yogyakarta
  Kategori yang tersedia HANYA: wisata, kuliner, ibadah
  Pemetaan kata pengguna ke kategori:
  - "masjid", "mushola", "sholat", "salat", "ibadah", "religi" → ibadah
  - "makan", "kuliner", "restoran", "warung", "seafood", "tempat makan" → kuliner
  - "wisata", "pantai", "candi", "taman", "snorkeling", "diving" → wisata
  Jika 2 kategori berbeda diminta → panggil tool DUA KALI dengan kategori berbeda.
  Jika lokasi tidak ada dalam daftar → JANGAN panggil tool, sampaikan data tidak tersedia.

- cari_transport: "KOTA" atau "KOTA,JENIS"
  Kota yang tersedia: Bali, Lombok, Yogyakarta
  Jenis yang tersedia: Shuttle Bandara, Rental Mobil, Rental Motor, Taksi
  Pemetaan:
  - "bus", "shuttle", "damri", "antar jemput" → Shuttle Bandara
  - "sewa mobil", "rental mobil", "mobil dengan supir", "eksklusif" → Rental Mobil
  - "sewa motor", "rental motor" → Rental Motor
  - "taksi", "grab", "ojek" → Taksi
  Jika jenis tidak disebutkan → gunakan kota saja tanpa jenis.
  Jika lokasi tidak ada dalam daftar → JANGAN panggil tool, sampaikan data tidak tersedia.

{context}"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

single_agent = create_tool_calling_agent(llm, tools, single_prompt)

single_agent_executor = AgentExecutor(
    agent=single_agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10
)

# ============================================================
# MULTI-AGENT SETUP (LangGraph)
# ============================================================

SUB_AGENT_SYSTEM = """Kamu adalah agen pencarian data perjalanan wisata Indonesia.
Gunakan tool yang tersedia untuk mencari data. DILARANG mengarang informasi.
Jika data tidak ditemukan, sampaikan DATA TIDAK DITEMUKAN dengan jelas.
Jawab dalam Bahasa Indonesia."""

flight_agent = create_react_agent(llm, [cari_penerbangan])
hotel_agent = create_react_agent(llm, [cari_hotel])
activity_agent = create_react_agent(llm, [cari_aktivitas])
transport_agent = create_react_agent(llm, [cari_transport])

class TravelState(TypedDict):
    query: str
    context: str
    flight_result: str
    hotel_result: str
    activity_result: str
    transport_result: str
    final_response: str

def run_flight_agent(state: TravelState):
    print("[MULTI-AGENT] Flight Agent berjalan...")
    try:
        flight_query = f"Dari query berikut, carikan informasi penerbangan yang relevan saja: {state['query']}"
        result = flight_agent.invoke({
            "messages": [
                SystemMessage(content=SUB_AGENT_SYSTEM),
                HumanMessage(content=flight_query)
            ]
        })
        return {"flight_result": result["messages"][-1].content}
    except Exception as e:
        return {"flight_result": f"Error: {str(e)}"}

def run_hotel_agent(state: TravelState):
    print("[MULTI-AGENT] Hotel Agent berjalan...")
    try:
        hotel_query = f"Dari query berikut, carikan informasi hotel yang relevan saja: {state['query']}"
        result = hotel_agent.invoke({
            "messages": [
                SystemMessage(content=SUB_AGENT_SYSTEM),
                HumanMessage(content=hotel_query)
            ]
        })
        return {"hotel_result": result["messages"][-1].content}
    except Exception as e:
        return {"hotel_result": f"Error: {str(e)}"}

def run_activity_agent(state: TravelState):
    print("[MULTI-AGENT] Activity Agent berjalan...")
    try:
        activity_query = f"Dari query berikut, carikan informasi aktivitas wisata yang relevan saja: {state['query']}"
        result = activity_agent.invoke({
            "messages": [
                SystemMessage(content=SUB_AGENT_SYSTEM),
                HumanMessage(content=activity_query)
            ]
        })
        return {"activity_result": result["messages"][-1].content}
    except Exception as e:
        return {"activity_result": f"Error: {str(e)}"}

def run_transport_agent(state: TravelState):
    print("[MULTI-AGENT] Transport Agent berjalan...")
    try:
        transport_query = f"Dari query berikut, carikan informasi transportasi yang relevan saja: {state['query']}"
        result = transport_agent.invoke({
            "messages": [
                SystemMessage(content=SUB_AGENT_SYSTEM),
                HumanMessage(content=transport_query)
            ]
        })
        return {"transport_result": result["messages"][-1].content}
    except Exception as e:
        return {"transport_result": f"Error: {str(e)}"}

def supervisor(state: TravelState):
    print("[MULTI-AGENT] Supervisor merangkum hasil...")
    summary_prompt = f"""Kamu adalah supervisor agen perjalanan wisata Indonesia.
Rangkum hasil pencarian dari 4 agen berikut menjadi rencana perjalanan yang lengkap dan terstruktur dalam Bahasa Indonesia.
Jangan mengarang data — hanya gunakan data yang sudah diberikan agen.
Jika ada agen yang mengembalikan DATA TIDAK DITEMUKAN, sampaikan juga ke user.

Query pengguna: {state['query']}

Hasil Agen Penerbangan:
{state.get('flight_result', 'Tidak dicari')}

Hasil Agen Hotel:
{state.get('hotel_result', 'Tidak dicari')}

Hasil Agen Aktivitas:
{state.get('activity_result', 'Tidak dicari')}

Hasil Agen Transportasi:
{state.get('transport_result', 'Tidak dicari')}

Rangkum semua hasil di atas. Tutup dengan estimasi total biaya jika data tersedia."""

    try:
        response = llm.invoke(summary_prompt)
        return {"final_response": response.content}
    except Exception as e:
        return {"final_response": f"Error supervisor: {str(e)}"}


# Build graph
graph = StateGraph(TravelState)
graph.add_node("flight_agent", run_flight_agent)
graph.add_node("hotel_agent", run_hotel_agent)
graph.add_node("activity_agent", run_activity_agent)
graph.add_node("transport_agent", run_transport_agent)
graph.add_node("supervisor", supervisor)

graph.set_entry_point("flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "activity_agent")
graph.add_edge("activity_agent", "transport_agent")
graph.add_edge("transport_agent", "supervisor")
graph.add_edge("supervisor", END)

multi_agent_graph = graph.compile()

# ============================================================
# REQUEST MODEL
# ============================================================
class TripRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

# ============================================================
# ENDPOINTS
# ============================================================
@app.get("/")
def read_root():
    return {
        "status": "Orchestrator Service Ready",
        "endpoints": {
            "single_agent": "/plan-trip",
            "multi_agent": "/plan-trip-multi"
        }
    }

@app.post("/plan-trip")
async def plan_trip(request: TripRequest):
    """Single Agent — satu AgentExecutor dengan 4 tools."""
    try:
        session = request.session_id or "default"
        context = get_relevant_context(session, request.query)

        start_time = time.time()

        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: single_agent_executor.invoke({
                "input": request.query,
                "context": context
            })
        )

        elapsed = round(time.time() - start_time, 2)
        response = result.get("output", "")

        save_conversation(session, request.query, response)
        print(f"[SINGLE AGENT] Response time: {elapsed}s | {response[:80]}...")

        return {
            "query": request.query,
            "session_id": session,
            "response": response,
            "mode": "single_agent",
            "response_time_seconds": elapsed
        }

    except Exception as e:
        print(f"[SINGLE AGENT] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plan-trip-multi")
async def plan_trip_multi(request: TripRequest):
    """Multi-Agent — 4 sub-agent independen + 1 supervisor (LangGraph)."""
    try:
        session = request.session_id or "default"
        context = get_relevant_context(session, request.query)

        start_time = time.time()

        initial_state: TravelState = {
            "query": request.query,
            "context": context,
            "flight_result": "",
            "hotel_result": "",
            "activity_result": "",
            "transport_result": "",
            "final_response": ""
        }

        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: multi_agent_graph.invoke(initial_state)
        )

        elapsed = round(time.time() - start_time, 2)
        response = result.get("final_response", "")

        save_conversation(session, request.query, response)
        print(f"[MULTI AGENT] Response time: {elapsed}s | {response[:80]}...")

        return {
            "query": request.query,
            "session_id": session,
            "response": response,
            "mode": "multi_agent",
            "response_time_seconds": elapsed,
            "agent_results": {
                "flight": result.get("flight_result", ""),
                "hotel": result.get("hotel_result", ""),
                "activity": result.get("activity_result", ""),
                "transport": result.get("transport_result", "")
            }
        }

    except Exception as e:
        print(f"[MULTI AGENT] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))