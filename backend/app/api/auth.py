"""
Authentication API routes — register, login, refresh, profile.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    UserRegister, UserLogin, TokenResponse, TokenRefresh, UserProfile
)
from app.services.auth_service import register_user, authenticate_user, generate_tokens, refresh_access_token
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user and return JWT tokens."""
    user = await register_user(data, db)
    return generate_tokens(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and return JWT tokens."""
    user = await authenticate_user(data.email, data.password, db)
    return generate_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    return await refresh_access_token(data.refresh_token, db)


@router.get("/me", response_model=UserProfile)
async def get_profile(user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return user
