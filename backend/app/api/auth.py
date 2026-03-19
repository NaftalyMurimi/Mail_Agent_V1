from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_supabase
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.utils.auth_utils import hash_password, verify_password, create_access_token
from app.utils.logger import logger
from datetime import datetime
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── Signup ─────────────────────────────────────────────
@router.post("/signup", status_code=201)
async def signup(request: SignupRequest):
    sb = get_supabase()
    logger.info(f"Signup attempt for {request.email}")

    # Check if email already exists
    existing = sb.table("users").select("id").eq("email", request.email).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = {
        "id":                str(uuid.uuid4()),
        "email":             request.email,
        "hashed_password":   hash_password(request.password),
        "full_name":         request.full_name,
        "subscription_tier": "free",
        "is_active":         True,
        "is_verified":       False,
        "created_at":        datetime.utcnow().isoformat(),
        "updated_at":        datetime.utcnow().isoformat(),
    }

    result = sb.table("users").insert(new_user).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")

    logger.info(f"New user created: {request.email}")
    return result.data[0]

# ── Login ──────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    sb = get_supabase()
    logger.info(f"Login attempt for {request.email}")

    # Find user
    result = sb.table("users").select("*").eq("email", request.email).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user = result.data[0]

    # Verify password
    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check account is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate token
    token = create_access_token({"sub": user["id"]})
    logger.info(f"Login successful for {request.email}")

    return {"access_token": token, "token_type": "bearer"}

# ── Logout ─────────────────────────────────────────────
@router.post("/logout")
async def logout():
    logger.info("User logged out")
    return {"message": "Successfully logged out"}