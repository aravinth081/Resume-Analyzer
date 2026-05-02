"""
SQLAlchemy ORM models — User, Subscription, and Tenant management.
Uses String-based UUIDs and JSON for SQLite compatibility.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, DateTime, Enum as SAEnum,
    Integer, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


def new_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    INDIVIDUAL = "individual"
    RECRUITER = "recruiter"
    ORG_ADMIN = "org_admin"
    ADMIN = "admin"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class User(Base):
    """Core user table — supports both B2C individuals and B2B recruiters."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="individual", nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Multi-tenant: users may belong to an organization
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    tenant = relationship("Tenant", back_populates="members")


class Tenant(Base):
    """Organization / company entity for multi-tenant isolation."""
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=new_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    members = relationship("User", back_populates="tenant")


class Subscription(Base):
    """User subscription tracking — controls feature access and usage limits."""
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     unique=True, nullable=False)
    tier = Column(String(20), default="free", nullable=False)

    # Usage counters (reset monthly)
    resumes_uploaded_this_month = Column(Integer, default=0)
    matches_this_month = Column(Integer, default=0)
    chat_messages_today = Column(Integer, default=0)
    last_usage_reset = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    current_period_end = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="subscription")


class ChatMessage(Base):
    """Chat history for the AI Career Copilot."""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="chat_messages")
