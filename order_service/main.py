import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Environment variables for service URLs
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8081")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8082")

# Mock Database
orders_db = []

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    status: str

@app.get("/status")
def get_status():
    return {"service": "order-service", "status": "up"}

@app.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    async with httpx.AsyncClient() as client:
        # 1. Verify User
        try:
            user_response = await client.get(f"{USER_SERVICE_URL}/users/{order.user_id}")
            if user_response.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
        except httpx.RequestError:
             raise HTTPException(status_code=503, detail="User service unavailable")

        # 2. Verify Product AND Decrease Stock (Atomic-ish)
        try:
            stock_response = await client.post(
                f"{PRODUCT_SERVICE_URL}/products/{order.product_id}/decrease_stock",
                json={"quantity": order.quantity}
            )
            if stock_response.status_code == 404:
                raise HTTPException(status_code=404, detail="Product not found")
            if stock_response.status_code == 400:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            if stock_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to update stock")
        except httpx.RequestError:
             raise HTTPException(status_code=503, detail="Product service unavailable")

    new_order = {
        "id": len(orders_db) + 1,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "confirmed"
    }
    orders_db.append(new_order)
    return new_order

@app.get("/orders", response_model=List[Order])
def get_orders():
    return orders_db

@app.get("/orders/user/{user_id}", response_model=List[Order])
def get_orders_by_user(user_id: int):
    return [o for o in orders_db if o["user_id"] == user_id]
