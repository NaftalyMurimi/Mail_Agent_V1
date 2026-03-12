from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.utils.auth_utils import hash_password, verify_password, create_access_token
from app.utils.logger import logger
from datetime import datetime
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── Signup ─────────────────────────────────────────────
@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for {request.email}")

    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        id              = uuid.uuid4(),
        email           = request.email,
        hashed_password = hash_password(request.password),
        full_name       = request.full_name,
        created_at      = datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user created: {request.email}")
    return new_user

# ── Login ──────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for {request.email}")

    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate token
    token = create_access_token({"sub": str(user.id)})
    logger.info(f"Login successful for {request.email}")

    return {"access_token": token, "token_type": "bearer"}

# ── Logout ─────────────────────────────────────────────
@router.post("/logout")
async def logout():
    # JWT is stateless — client simply discards the token
    logger.info("User logged out")
    return {"message": "Successfully logged out"}