from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Mock Database
products_db = [
    {"id": 101, "name": "Laptop", "price": 999.99, "stock": 10},
    {"id": 102, "name": "Smartphone", "price": 499.99, "stock": 20},
    {"id": 103, "name": "Headphones", "price": 199.99, "stock": 5},
]

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int

class Product(ProductCreate):
    id: int

class StockUpdate(BaseModel):
    quantity: int

@app.get("/status")
def get_status():
    return {"service": "product-service", "status": "up"}

@app.post("/products", response_model=Product)
def create_product(product: ProductCreate):
    new_id = max(p["id"] for p in products_db) + 1 if products_db else 101
    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }
    products_db.append(new_product)
    return new_product

@app.get("/products", response_model=List[Product])
def get_products():
    return products_db

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products/{product_id}/decrease_stock")
def decrease_stock(product_id: int, update: StockUpdate):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < update.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    product["stock"] -= update.quantity
    return {"id": product_id, "new_stock": product["stock"]}
