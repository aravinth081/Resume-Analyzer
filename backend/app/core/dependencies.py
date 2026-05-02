"""
FastAPI dependency injection — current user extraction, role checks, subscription limits.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import jwt

from app.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole, SubscriptionTier
from app.models.resume import Resume

security_scheme = HTTPBearer()

# ── Subscription limits map ──
TIER_LIMITS = {
    SubscriptionTier.FREE: {
        "resumes_per_month": 3,
        "matches_per_month": 1,
        "chat_per_day": 5,
        "max_versions": 2,
    },
    SubscriptionTier.PRO: {
        "resumes_per_month": 25,
        "matches_per_month": 10,
        "chat_per_day": 50,
        "max_versions": 10,
    },
    SubscriptionTier.PREMIUM: {
        "resumes_per_month": 999999,
        "matches_per_month": 999999,
        "chat_per_day": 999999,
        "max_versions": 999999,
    },
    SubscriptionTier.ENTERPRISE: {
        "resumes_per_month": 999999,
        "matches_per_month": 999999,
        "chat_per_day": 999999,
        "max_versions": 999999,
    },
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate the current user from the JWT access token.
    Returns the full User ORM object with subscription eagerly loaded.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


async def require_role(*roles: UserRole):
    """
    Factory for role-based access control.
    Usage: Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN))
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role.value}' is not authorized for this action"
            )
        return user
    return role_checker


async def check_upload_limit(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Check if the user has remaining resume upload quota this month."""
    from app.models.user import Subscription
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = result.scalar_one_or_none()

    tier = sub.tier if sub else SubscriptionTier.FREE
    limit = TIER_LIMITS[tier]["resumes_per_month"]
    used = sub.resumes_uploaded_this_month if sub else 0

    if used >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly resume upload limit reached ({limit}). Upgrade your plan."
        )
    return user
