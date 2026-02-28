from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="API Gateway Service")

ORCHESTRATOR_URL = "http://127.0.0.1:8001"

@app.get("/")
def read_root():
    """Health check endpoint for the API Gateway."""
    return {"status": "API Gateway Ready", "message": "Selamat datang di Travel Planner API Gateway"}

@app.get("/api/chat")
async def chat_with_ai(query: str):
    """
    Main entry point for the frontend client.
    Asynchronously forwards the natural language query to the Orchestrator Service.
    """
    # TODO: Integrasi pengecekan Auth Service sesuai desain arsitektur (Sub-bab 3.2.1).
    # Validate user token before forwarding request to the AI logic.
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{ORCHESTRATOR_URL}/plan-trip", params={"query": query})
            
            if response.status_code == 200:
                return response.json()
                
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Orchestrator Error ({response.status_code}): {response.text}"
            )
            
    except httpx.RequestError as e:
        # Enforcing fault isolation mechanism
        raise HTTPException(
            status_code=503, 
            detail=f"Service Unavailable: Tidak dapat terhubung ke Orchestrator. Error: {str(e)}"
        )