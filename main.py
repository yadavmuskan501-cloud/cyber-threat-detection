
import os
import sqlite3
import bcrypt

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from jose import JWTError, jwt


# ================= FASTAPI APPLICATION =================

app = FastAPI(
    title="SENTINEL AI - Cyber Threat Detection & SOC",
    description="""
# SentinelAI API Documentation

SentinelAI is a cybersecurity monitoring and authentication
platform designed to support Security Operations Center (SOC)
workflows.

## Core Features

- **Authentication:** Secure user registration and login.
- **JWT Security:** Token-based authentication.
- **RBAC:** Role-Based Access Control for Admin and Analyst users.
- **User Management:** Protected user profile and administration.
- **Threat Monitoring:** Role-protected threat monitoring endpoints.

## Authentication Instructions

1. Register an account using the registration endpoint.
2. Log in using your registered username and password.
3. Copy the returned access token.
4. Click the **Authorize** button in Swagger UI.
5. Enter your JWT access token using the Bearer authentication scheme.
6. Access the protected endpoints.

Protected endpoints require a valid JWT access token.

## User Roles

- **Admin:** Access to administrative and user-management endpoints.
- **Analyst:** Access to authorized threat-monitoring endpoints.
""",
    version="1.2.0",
    openapi_tags=[
        {
            "name": "Frontend",
            "description": "SentinelAI frontend application routes."
        },
        {
            "name": "Authentication",
            "description": "User registration, login and profile management."
        },
        {
            "name": "Role-Based Access Control",
            "description": "Endpoints protected by user roles and permissions."
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= CONFIGURATION =================

# Set SENTINEL_SECRET_KEY in the environment for real deployments.
# The fallback preserves compatibility with existing development tokens.
SECRET_KEY = os.getenv(
    "SENTINEL_SECRET_KEY",
    "SENTINEL_AI_CRYPTO_SECRET_KEY_9942_NEVER_SHARE"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

DB_NAME = "sentinel.db"

security = HTTPBearer()


# ================= ROLES =================

ROLE_ADMIN = "Admin"
ROLE_ANALYST = "Analyst"

# Existing project accounts may use "Incident Commander".
# Treat that legacy role as Admin until accounts are migrated.
ADMIN_ROLES = {ROLE_ADMIN, "Incident Commander"}


# ================= DATABASE INITIALIZATION =================

def init_database():
    conn = sqlite3.connect(DB_NAME)

    try:
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

        # Preserve the existing development account.
        cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            ("analyst1",)
        )

        if not cursor.fetchone():
            salt = bcrypt.gensalt(rounds=12)

            default_hash = bcrypt.hashpw(
                "Sentinel2026!".encode("utf-8"),
                salt
            ).decode("utf-8")

            cursor.execute("""
                INSERT INTO users
                (username, email, hashed_password, role)
                VALUES (?, ?, ?, ?)
            """, (
                "analyst1",
                "analyst1@sentinelai.com",
                default_hash,
                "Incident Commander"
            ))

            conn.commit()

    finally:
        conn.close()


init_database()


# ================= PASSWORD UTILITIES =================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)

    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ================= JWT UTILITIES =================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:

    to_encode = data.copy()

    now = datetime.now(timezone.utc)

    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "iat": now
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict:

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Session Token Expired or Invalid Signature. "
                "Please authenticate again."
            )
        )


# ================= AUTHENTICATION DEPENDENCY =================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = decode_access_token(token)

    username = payload.get("sub")

    if not username or not isinstance(username, str):
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload."
        )

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, email, role
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

    finally:
        conn.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )

    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "role": user[3]
    }


# ================= RBAC DEPENDENCIES =================

async def require_admin(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Admin privileges required."
        )

    return current_user


async def require_analyst_or_admin(
    current_user: dict = Depends(get_current_user)
):

    allowed_roles = ADMIN_ROLES | {ROLE_ANALYST}

    if current_user["role"] not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Insufficient permissions."
        )

    return current_user


# ================= PYDANTIC SCHEMAS =================

class RegisterRequest(BaseModel):

    username: str = Field(
        ...,
        description="Unique username for the new SentinelAI account.",
        examples=["analyst2"]
    )

    email: EmailStr = Field(
        ...,
        description="Valid email address of the user.",
        examples=["analyst2@example.com"]
    )

    password: str = Field(
        ...,
        description="Account password. Must contain at least 8 characters.",
        examples=["ExamplePass123!"]
    )


class LoginRequest(BaseModel):

    username: str = Field(
        ...,
        description="Registered SentinelAI username.",
        examples=["analyst1"]
    )

    password: str = Field(
        ...,
        description="Password associated with the registered account.",
        examples=["ExamplePass123!"]
    )


# ================= FRONTEND ROUTES =================

@app.get(
    "/",
    summary="Open Login Page",
    description="Serves the SentinelAI login interface.",
    tags=["Frontend"],
    response_description="SentinelAI login HTML page."
)
async def serve_login():
    return FileResponse("login.html")


@app.get(
    "/dashboard",
    summary="Open Dashboard",
    description="Serves the SentinelAI dashboard interface.",
    tags=["Frontend"],
    response_description="SentinelAI dashboard HTML page."
)
async def serve_dashboard():
    return FileResponse("dashboard.html")


# ================= REGISTRATION =================

@app.post(
    "/api/auth/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a New User",
    description="""
Creates a new SentinelAI user account.

The user must provide a unique username, valid email address
and password containing at least 8 characters.

Public registration automatically assigns the Analyst role.
Users cannot assign themselves Admin privileges.
""",
    tags=["Authentication"],
    response_description="New Analyst account created successfully.",
    responses={
        400: {
            "description": "Username or email already exists, or invalid registration data."
        },
        422: {
            "description": "Request validation failed."
        }
    }
)
async def register_user(user: RegisterRequest):

    username = user.username.strip().lower()
    email = str(user.email).strip().lower()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty."
        )

    if len(user.password) < 8:
        raise HTTPException(
            status_code=400,
            detail=(
                "Security Policy: Password must be "
                "at least 8 characters."
            )
        )

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM users
            WHERE username = ? OR email = ?
        """, (username, email))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Conflict: Username or Email "
                    "is already registered."
                )
            )

        hashed_pwd = hash_password(user.password)

        # SECURITY: Public registration cannot assign Admin.
        cursor.execute("""
            INSERT INTO users
            (username, email, hashed_password, role)
            VALUES (?, ?, ?, ?)
        """, (
            username,
            email,
            hashed_pwd,
            ROLE_ANALYST
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Username or Email already exists."
        )

    finally:
        conn.close()

    return {
        "status": "Success",
        "message": (
            f"Analyst account '{username}' "
            "created successfully."
        ),
        "role": ROLE_ANALYST
    }


# ================= LOGIN =================

@app.post(
    "/api/auth/login",
    summary="Authenticate User",
    description="""
Authenticates an existing SentinelAI user.

Provide the registered username and password.

On successful authentication, the API returns a JWT access token.
Use this token to access protected API endpoints through
the Swagger Authorize button.
""",
    tags=["Authentication"],
    response_description="Authentication successful with JWT access token.",
    responses={
        401: {
            "description": "Invalid username or password."
        },
        422: {
            "description": "Request validation failed."
        }
    }
)
async def login(credentials: LoginRequest):

    username = credentials.username.strip().lower()

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, email,
                   hashed_password, role
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

    finally:
        conn.close()

    if not user or not verify_password(
        credentials.password,
        user[3]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Access Denied: Invalid Username "
                "or Cryptographic Passkey."
            )
        )

    token_payload = {
        "sub": user[1],
        "email": user[2],
        "role": user[4]
    }

    jwt_token = create_access_token(
        data=token_payload
    )

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


# ================= PROTECTED PROFILE =================

@app.get(
    "/api/auth/me",
    summary="Get Current User Profile",
    description="""
Returns the profile of the currently authenticated user.

Requires a valid JWT Bearer access token.

Click Authorize in Swagger UI and provide the access token
obtained from the login endpoint.
""",
    tags=["Authentication"],
    response_description="Authenticated user's profile.",
    responses={
        401: {
            "description": "Invalid, expired or unrecognized JWT token."
        },
        403: {
            "description": "Authentication credentials are missing."
        }
    }
)
async def get_my_profile(
    current_user: dict = Depends(get_current_user)
):

    return {
        "status": "Authorized",
        "profile": current_user
    }


# ================= RBAC PROTECTED ENDPOINTS =================

# Both Admin and Analyst can view this information.
@app.get(
    "/api/rbac/threats",
    summary="View Threat Monitoring Data",
    description="""
Provides access to threat monitoring information.

Both Admin and Analyst roles are permitted to access this endpoint.
A valid JWT Bearer token is required.
""",
    tags=["Role-Based Access Control"],
    response_description="Threat monitoring access information.",
    responses={
        401: {
            "description": "Invalid or expired authentication token."
        },
        403: {
            "description": "Authentication credentials missing or insufficient permissions."
        }
    }
)
async def view_threats(
    current_user: dict = Depends(require_analyst_or_admin)
):

    return {
        "status": "Authorized",
        "message": "Threat monitoring access granted.",
        "role": current_user["role"],
        "threats": []
    }


# Only Admin can access this endpoint.
@app.get(
    "/api/rbac/admin",
    summary="Access Admin Dashboard",
    description="""
Provides access to administrative dashboard functionality.

Only users with the Admin role or the legacy
Incident Commander role can access this endpoint.

A valid JWT Bearer token is required.
""",
    tags=["Role-Based Access Control"],
    response_description="Administrative access confirmation.",
    responses={
        401: {
            "description": "Invalid or expired authentication token."
        },
        403: {
            "description": "Admin privileges required."
        }
    }
)
async def admin_dashboard(
    current_user: dict = Depends(require_admin)
):

    return {
        "status": "Authorized",
        "message": "Admin-only access granted.",
        "role": current_user["role"]
    }


# Only Admin can view registered user summaries.
@app.get(
    "/api/rbac/users",
    summary="List Registered Users",
    description="""
Returns a summary of registered SentinelAI users.

Only users with the Admin role or the legacy
Incident Commander role can access this endpoint.

Passwords and password hashes are not returned.
A valid JWT Bearer token is required.
""",
    tags=["Role-Based Access Control"],
    response_description="List of registered user summaries.",
    responses={
        401: {
            "description": "Invalid or expired authentication token."
        },
        403: {
            "description": "Admin privileges required."
        }
    }
)
async def list_users(
    current_user: dict = Depends(require_admin)
):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, email, role
            FROM users
            ORDER BY id
        """)

        rows = cursor.fetchall()

    finally:
        conn.close()

    users = [
        {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "role": row[3]
        }
        for row in rows
    ]

    return {
        "status": "Authorized",
        "users": users
    }
