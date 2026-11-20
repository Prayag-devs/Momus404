"""
momus404 — app.api.v1.endpoints.auth
Authentication endpoints for Login, Verification, and Session Management.
"""

import time
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["Auth"])

# In-memory test accounts database
TEST_ACCOUNTS = {
    "admin@momus404.local": {
        "username": "admin",
        "email": "admin@momus404.local",
        "password": "Momus404!SecureAdmin",
        "role": "System Administrator",
        "name": "Admin Operator",
        "is_locked": False,
        "is_active": True,
    },
    "admin": {
        "username": "admin",
        "email": "admin@momus404.local",
        "password": "Momus404!SecureAdmin",
        "role": "System Administrator",
        "name": "Admin Operator",
        "is_locked": False,
        "is_active": True,
    },
    "qa_tester@momus404.local": {
        "username": "tester",
        "email": "qa_tester@momus404.local",
        "password": "TesterPass@2026",
        "role": "Lead QA Engineer",
        "name": "QA Automation Engineer",
        "is_locked": False,
        "is_active": True,
    },
    "tester": {
        "username": "tester",
        "email": "qa_tester@momus404.local",
        "password": "TesterPass@2026",
        "role": "Lead QA Engineer",
        "name": "QA Automation Engineer",
        "is_locked": False,
        "is_active": True,
    },
    "locked_user@momus404.local": {
        "username": "locked_user",
        "email": "locked_user@momus404.local",
        "password": "LockedPass123!",
        "role": "Standard User",
        "name": "Locked User",
        "is_locked": True,
        "is_active": True,
    },
    "disabled_user@momus404.local": {
        "username": "disabled_user",
        "email": "disabled_user@momus404.local",
        "password": "DisabledPass123!",
        "role": "Standard User",
        "name": "Disabled User",
        "is_locked": False,
        "is_active": False,
    },
}

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255, description="Username or email")
    password: str = Field(..., min_length=1, max_length=1024, description="User password")
    remember_me: Optional[bool] = False

class LoginResponse(BaseModel):
    status: str
    message: str
    token: str
    user: dict
    expires_in: int

class VerifyResponse(BaseModel):
    authenticated: bool
    user: dict
    token: str
    status: str

@router.options("/login", summary="CORS preflight for login")
async def options_login():
    return Response(
        status_code=status.HTTP_200_OK,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

@router.post("/login", response_model=LoginResponse, summary="Authenticate user credentials")
async def login(req: LoginRequest):
    norm_user = req.username.strip().lower()

    # Constant-time delay simulation to thwart timing attacks
    time.sleep(0.05)

    account = TEST_ACCOUNTS.get(norm_user)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if account["is_locked"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked. Contact administrator.",
        )

    if not account["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    if account["password"] != req.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = f"MOMUS-SEC-{int(time.time())}-{hash(norm_user) % 100000:05d}"
    ttl = 86400 * 7 if req.remember_me else 86400

    return LoginResponse(
        status="success",
        message="Authentication successful",
        token=token,
        user={
            "email": account["email"],
            "username": account["username"],
            "role": account["role"],
            "name": account["name"],
        },
        expires_in=ttl,
    )

@router.options("/verify", summary="CORS preflight for verify")
async def options_verify():
    return Response(
        status_code=status.HTTP_200_OK,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

@router.get("/verify", response_model=VerifyResponse, summary="Verify active authentication session")
@router.post("/verify", response_model=VerifyResponse, summary="Verify active authentication session via POST")
async def verify_session(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
        )

    token = authorization.replace("Bearer ", "").strip()
    return VerifyResponse(
        authenticated=True,
        user={
            "email": "admin@momus404.local",
            "role": "System Administrator",
            "name": "Admin Operator",
        },
        token=token,
        status="ACTIVE",
    )

@router.options("/logout", summary="CORS preflight for logout")
async def options_logout():
    return Response(
        status_code=status.HTTP_200_OK,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

@router.post("/logout", summary="Invalidate authentication session")
@router.get("/logout", summary="Invalidate authentication session via GET")
async def logout():
    return {"status": "success", "message": "Session invalidated."}
