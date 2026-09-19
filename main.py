import os
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt

app = FastAPI(title="SENTINEL AI - Cryptographic Authentication & SOC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CRYPTOGRAPHIC CONFIGURATION =================
# In production, store this in an environment variable (.env)
SECRET_KEY = "SENTINEL_AI_CRYPTO_SECRET_KEY_9942_NEVER_SHARE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Token valid for 2 hours

DB_NAME = "sentinel.db"
security = HTTPBearer()

# ================= DATABASE INITIALIZATION =================
def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Analyst',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Pre-seed default master account if empty
    cursor.execute("SELECT * FROM users WHERE username = 'analyst1'")
    if not cursor.fetchone():
        salt = bcrypt.gensalt(rounds=12)
        default_hash = bcrypt.hashpw("Sentinel2026!".encode('utf-8'), salt).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, role) VALUES (?, ?, ?, ?)",
            ("analyst1", "analyst1@sentinelai.com", default_hash, "Incident Commander")
        )
        conn.commit()
    conn.close()

init_database()

# ================= PASSWORD HASHING UTILITIES =================
def hash_password(password: str) -> str:
    """Generates a cryptographic salted Bcrypt hash."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored salted hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ================= JWT TOKEN UTILITIES =================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session Token Expired or Invalid Signature. Please authenticate again."
        )

# Dependency: Enforce JWT validation on protected routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")
    
    return {"id": user[0], "username": user[1], "email": user[2], "role": user[3]}

# ================= PYDANTIC SCHEMAS =================
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "Analyst"

class LoginRequest(BaseModel):
    username: str
    password: str

# ================= API ENDPOINTS =================

@app.get("/")
async def serve_login():
    return FileResponse("login.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("dashboard.html")

# 1. REGISTER NEW USER (Saves to SQLite with Bcrypt hash)
@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: RegisterRequest):
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Security Policy: Password must be at least 8 characters.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check for existing username or email
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (user.username, user.email))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Conflict: Username or Email is already registered.")

    # Hash password with Bcrypt
    hashed_pwd = hash_password(user.password)

    # Insert into database
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, role) VALUES (?, ?, ?, ?)",
        (user.username.strip().lower(), user.email.strip().lower(), hashed_pwd, user.role)
    )
    conn.commit()
    conn.close()

    return {"status": "Success", "message": f"Analyst account '{user.username}' created successfully."}

# 2. LOGIN (Verifies Hash & Issues Signed JWT)
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, hashed_password, role FROM users WHERE username = ?", (credentials.username.strip().lower(),))
    user = cursor.fetchone()
    conn.close()

    # Verify user exists and check Bcrypt password
    if not user or not verify_password(credentials.password, user[3]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: Invalid Username or Cryptographic Passkey."
        )

    # Issue JWT
    token_payload = {
        "sub": user[1],
        "email": user[2],
        "role": user[4]
    }
    jwt_token = create_access_token(data=token_payload)

    return {
        "status": "Authenticated",
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "username": user[1],
            "email": user[2],
            "role": user[4]
        }
    }

# 3. PROTECTED ROUTE (Requires valid JWT header to access)
@app.get("/api/auth/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {"status": "Authorized", "profile": current_user}