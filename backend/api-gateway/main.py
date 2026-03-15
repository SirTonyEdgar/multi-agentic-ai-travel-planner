import httpx
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="API Gateway", version="1.0.0")

ORCHESTRATOR_URL = "http://127.0.0.1:8001"


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