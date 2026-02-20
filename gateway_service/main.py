import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Environment variables for service URLs
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8081")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8082")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order_service:8083")
STRESS_SERVICE_URL = os.getenv("STRESS_SERVICE_URL", "http://cpu_stress_service:8084")

# Inside your gateway function...

# ...

@app.get("/status")
def get_status():
    return {"service": "gateway-service", "status": "up"}

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(path_name: str, request: Request):
    
    # Simple routing logic based on path prefix
    if path_name.startswith("users") or path_name.startswith("login") or path_name.startswith("register"):
        target_url = f"{USER_SERVICE_URL}/{path_name}"
    elif path_name.startswith("products"):
        target_url = f"{PRODUCT_SERVICE_URL}/{path_name}"
    elif path_name.startswith("orders"):
        target_url = f"{ORDER_SERVICE_URL}/{path_name}"
    elif path_name.startswith("stress"):
        target_url = f"{STRESS_SERVICE_URL}/{path_name}"
    else:
        raise HTTPException(status_code=404, detail="Route not found")

    async with httpx.AsyncClient() as client:
        try:
            # Forward the request to the target service
            response = await client.request(
                method=request.method,
                url=target_url,
                content=await request.body(),
                params=request.query_params,
                headers=request.headers, # Forward headers if needed, be careful with Host header
            )
            return JSONResponse(status_code=response.status_code, content=response.json())
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service unavailable")

