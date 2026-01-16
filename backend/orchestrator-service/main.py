import os
from fastapi import FastAPI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from tools import cari_hotel, cari_penerbangan

# 1. Setup Environment
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI(title="Orchestrator Service (Linear LangChain)")

# 2. Setup Model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0,            
    google_api_key=GOOGLE_API_KEY
)

# 3. Definisikan Tools
tools = [cari_hotel, cari_penerbangan]

# 4. Ambil Prompt ReAct Standar
prompt = hub.pull("hwchase17/react")

# Modifikasi Prompt agar AI paham format alat yang baru
prompt.template = """
Kamu adalah Agen Perjalanan Wisata yang profesional.

INSTRUKSI WAJIB:
1. Jawablah pertanyaan user sebaik mungkin dalam Bahasa Indonesia.
2. Kamu memiliki akses ke alat berikut:
{tools}

3. ATURAN PENGGUNAAN ALAT (PENTING):
   - Jika menggunakan `cari_hotel`: Input hanya nama kota (contoh: "Bali").
   - Jika menggunakan `cari_penerbangan`: Input WAJIB format "ASAL,TUJUAN" (contoh: "CGK,DPS"). Jangan dipisah spasi, pakai koma.

4. Gunakan format berpikir ReAct:

Question: pertanyaan input dari user
Thought: pikirkan apa yang harus dilakukan
Action: pilih salah satu dari [{tool_names}]
Action Input: input untuk alat tersebut
Observation: hasil dari alat
... (ulangi Thought/Action/Observation jika perlu)
Thought: Saya sudah punya semua data
Final Answer: jawaban akhir yang detail (Sebutkan Nama Hotel, Maskapai, Harga, Jam).

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

# 5. Buat Agen Linear
agent = create_react_agent(llm, tools, prompt)

# 6. Buat Eksekutor
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True # Ini penting agar kalau error format, dia tidak crash
)

@app.get("/")
def read_root():
    return {"status": "AI Agent Ready (Linear Version)"}

@app.get("/plan-trip")
def plan_trip(query: str):
    try:
        print(f"--- Menerima Query: {query} ---")
        
        # Eksekusi agen
        result = agent_executor.invoke({"input": query})
        
        last_message = result["output"]
        
        print(f"--- Jawaban AI: {last_message[:100]}... ---")
        
        return {
            "query": query,
            "response": last_message
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}