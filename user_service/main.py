from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Mock Database
users_db = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "wallet": 100.0},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "wallet": 50.0},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "wallet": 1200.0},
]

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    wallet: float

class LoginRequest(BaseModel):
    email: str

@app.get("/status")
def get_status():
    return {"service": "user-service", "status": "up"}

@app.post("/register", response_model=User)
def register(user: UserCreate):
    new_id = max(u["id"] for u in users_db) + 1 if users_db else 1
    new_user = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
        "wallet": 1000.0  # Sign-up bonus
    }
    users_db.append(new_user)
    return new_user

@app.post("/login")
def login(request: LoginRequest):
    user = next((u for u in users_db if u["email"] == request.email), None)
    if user:
        return {"id": user["id"], "name": user["name"]}
    raise HTTPException(status_code=401, detail="Invalid email")

@app.get("/users", response_model=List[User])
def get_users():
    return users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = next((user for user in users_db if user["id"] == user_id), None)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
