"""
Pydantic schemas for User-related request/response models.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.user import UserRole, SubscriptionTier


# ── Auth Schemas ──

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.INDIVIDUAL


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


# ── User Schemas ──

class UserProfile(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    tenant_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


# ── Subscription Schemas ──

class SubscriptionInfo(BaseModel):
    tier: SubscriptionTier
    resumes_uploaded_this_month: int
    matches_this_month: int
    chat_messages_today: int
    current_period_end: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionUpgrade(BaseModel):
    tier: SubscriptionTier
    payment_method_id: Optional[str] = None
