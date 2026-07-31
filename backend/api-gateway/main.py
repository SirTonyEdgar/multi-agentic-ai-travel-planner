import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

def resolve_url(env_value: str) -> str:
    """Terima bare hostname (mis. dari Render 'fromService: property: host')
    atau full URL (mis. 'http://orchestrator-service:8001' di docker-compose lokal)."""
    if env_value.startswith("http://") or env_value.startswith("https://"):
        return env_value
    return f"https://{env_value}"

app = FastAPI(title="API Gateway", version="1.0.0")

# Daftar origin frontend yang boleh akses API ini, dipisah koma.
# Default mencakup dev server lokal (docker-compose / npm run dev).
_default_origins = "http://localhost:5173,http://localhost:5174"
ALLOWED_ORIGINS = [resolve_url(o.strip()) for o in os.getenv("ALLOWED_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # tidak ada cookie/auth di alur ini, aman dipakai bareng origin "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Di docker-compose, "orchestrator-service" adalah nama service di jaringan internal.
# Di Render (atau host lain), override lewat env var ORCHESTRATOR_URL — boleh diisi
# bare hostname (auto dari Render) atau full URL.
ORCHESTRATOR_URL = resolve_url(os.getenv("ORCHESTRATOR_URL", "http://orchestrator-service:8001"))

@app.get("/")
def health_check():
    return {"status": "API Gateway Ready"}

@app.get("/api/chat")
async def chat(query: str = Query(...), session_id: str | None = None):
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{ORCHESTRATOR_URL}/plan-trip",
                json={"query": query, "session_id": session_id}
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Orchestrator unavailable: {str(e)}"
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json().get("detail", "Orchestrator error")
        )

    return response.json()