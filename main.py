
import os
from pymongo.errors import DuplicateKeyError
from database import (
    users_collection,
    get_next_user_id,
    init_database as initialize_mongodb
)
import bcrypt

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from ml.predict import predict_threat

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
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# ================= CONFIGURATION =================

# Set SENTINEL_SECRET_KEY in the environment for real deployments.
# The fallback preserves compatibility with existing development tokens.
from database import config as secure_config

SECRET_KEY = secure_config.get("SENTINEL_SECRET_KEY")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SENTINEL_SECRET_KEY must be configured securely."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120



security = HTTPBearer()


# ================= ROLES =================

ROLE_ADMIN = "Admin"
ROLE_ANALYST = "Analyst"

# Existing project accounts may use "Incident Commander".
# Treat that legacy role as Admin until accounts are migrated.
ADMIN_ROLES = {ROLE_ADMIN, "Incident Commander"}


# ================= DATABASE INITIALIZATION =================

def init_database():
    initialize_mongodb()



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

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub")

    if not username or not isinstance(username, str):
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload."
        )

    user = users_collection.find_one(
        {"username": username},
        {"_id": 0, "id": 1, "username": 1,
         "email": 1, "role": 1}
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )

    return user



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
def register_user(user: RegisterRequest):

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
            detail="Security Policy: Password must be at least 8 characters."
        )

    existing = users_collection.find_one({
        "$or": [
            {"username": username},
            {"email": email}
        ]
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Conflict: Username or Email is already registered."
        )

    try:
        users_collection.insert_one({
            "id": get_next_user_id(),
            "username": username,
            "email": email,
            "hashed_password": hash_password(user.password),
            "role": ROLE_ANALYST,
            "created_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

    except DuplicateKeyError:
        raise HTTPException(
            status_code=400,
            detail="Username or Email already exists."
        )

    return {
        "status": "Success",
        "message": f"Analyst account '{username}' created successfully.",
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
def login(credentials: LoginRequest):

    username = credentials.username.strip().lower()

    user = users_collection.find_one(
        {"username": username}
    )

    if not user or not verify_password(
        credentials.password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Access Denied: Invalid Username or Cryptographic Passkey."
        )

    token_payload = {
        "sub": user["username"],
        "email": user["email"],
        "role": user["role"]
    }

    jwt_token = create_access_token(data=token_payload)

    return {
        "status": "Authenticated",
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
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
def list_users(
    current_user: dict = Depends(require_admin)
):

    users = list(users_collection.find(
        {},
        {"_id": 0, "id": 1, "username": 1,
         "email": 1, "role": 1}
    ).sort("id", 1))

    return {
        "status": "Authorized",
        "users": users
    }





# ================= ML THREAT PREDICTION =================

class ThreatPredictionRequest(BaseModel):
    features: dict[str, Any] = Field(
        ...,
        description="All 78 network traffic features used during ML training"
    )


@app.post(
    "/api/ml/predict",
    summary="Predict Cyber Threat Using Random Forest",
    description=(
        "Classifies network traffic as BENIGN or ATTACK "
        "using the trained Random Forest model. "
        "Requires JWT authentication and Admin or Analyst role."
    ),
    tags=["Machine Learning"],
    responses={
        400: {"description": "Invalid or missing network traffic features"},
        401: {"description": "Invalid or expired JWT token"},
        403: {"description": "Insufficient permissions"},
        503: {"description": "ML model unavailable"}
    }
)
async def predict_network_threat(
    request: ThreatPredictionRequest,
    current_user: dict = Depends(require_analyst_or_admin)
):
    try:
        result = predict_threat(request.features)

        return {
            "status": "success",
            "model": "Random Forest",
            "result": result
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Trained ML model is unavailable."
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
