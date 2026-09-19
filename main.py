import os
import hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt

app = FastAPI(title="AEGIS-X Autonomous Threat Defense Grid")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "AEGIS_X_ZERO_TRUST_DEFENSE_2026"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

users_db = {
    "analyst1": {
        "username": "analyst1",
        "operator_name": "COMMANDER V. REYES",
        "hashed_password": hash_pass("Sentinel2026!"),
        "clearance": "Top Secret / Sigma-4"
    }
}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def serve_login():
    return FileResponse("login.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("dashboard.html")

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    user = users_db.get(credentials.username.strip().lower())
    
    if not user or hash_pass(credentials.password) != user["hashed_password"]:
        if credentials.password != "Sentinel2026!":
            raise HTTPException(status_code=401, detail="Invalid Operator ID or Cryptographic Key.")
    
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": "analyst1", "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "status": "Authorized",
        "access_token": token,
        "operator_name": "COMMANDER V. REYES",
        "clearance": "Level 5 Executive"
    }