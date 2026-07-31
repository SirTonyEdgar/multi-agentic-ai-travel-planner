import os
import httpx
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Integration Service", version="1.0.0")

def resolve_url(env_value: str) -> str:
    """Terima bare hostname (dari Render) atau full URL (docker-compose lokal)."""
    if env_value.startswith("http://") or env_value.startswith("https://"):
        return env_value
    return f"https://{env_value}"

MOCK_API_URL = resolve_url(os.getenv("MOCK_API_URL", "http://mock-api:8002"))

@app.get("/")
def health_check():
    return {"status": "Integration Service Ready"}

@app.get("/flights")
async def get_flights(
    origin: str = Query(...),
    destination: str = Query(...)
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{MOCK_API_URL}/flights",
                params={"origin": origin.upper(), "destination": destination.upper()}
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Mock API unavailable: {str(e)}")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=response.json().get("detail"))
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Upstream error")

    return response.json()

@app.get("/hotels")
async def get_hotels(
    location: str = Query(...),
    max_price: int = Query(None)
):
    params = {"location": location}
    if max_price:
        params["max_price"] = max_price

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{MOCK_API_URL}/hotels", params=params)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Mock API unavailable: {str(e)}")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=response.json().get("detail"))
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Upstream error")

    return response.json()

@app.get("/activities")
async def get_activities(
    location: str = Query(...),
    category: str = Query(None)
):
    params = {"location": location}
    if category:
        params["category"] = category

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{MOCK_API_URL}/activities", params=params)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Mock API unavailable: {str(e)}")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=response.json().get("detail"))
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Upstream error")

    return response.json()

@app.get("/transport")
async def get_transport(
    location: str = Query(...),
    type: str = Query(None)
):
    params = {"location": location}
    if type:
        params["type"] = type

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{MOCK_API_URL}/transport", params=params)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Mock API unavailable: {str(e)}")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=response.json().get("detail"))
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Upstream error")

    return response.json()