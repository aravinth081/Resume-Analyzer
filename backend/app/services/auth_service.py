"""
Authentication service — handles registration, login, and token management.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.user import User, Subscription, SubscriptionTier
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserRegister, TokenResponse
from app.config import settings
from fastapi import HTTPException, status
import jwt


async def register_user(data: UserRegister, db: AsyncSession) -> User:
    """Register a new user with a free subscription."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    await db.flush()  # Get the user ID

    # Create default free subscription
    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.FREE,
    )
    db.add(subscription)
    await db.flush()

    return user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    """Verify credentials and return user."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    return user


def generate_tokens(user: User) -> TokenResponse:
    """Generate access and refresh tokens for a user."""
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        }
    )
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> TokenResponse:
    """Generate new tokens from a valid refresh token."""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return generate_tokens(user)
