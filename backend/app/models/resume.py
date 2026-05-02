"""
SQLAlchemy ORM models — Resume, ResumeVersion, and parsed data storage.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, DateTime, Integer, Float, Text,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


def new_uuid():
    return str(uuid.uuid4())


class ResumeStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    tenant_id = Column(String(36), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)
    status = Column(String(20), default="uploaded", nullable=False)
    version = Column(Integer, default=1)

    parsed_data = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)

    overall_score = Column(Float, nullable=True)
    section_scores = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume",
                            cascade="all, delete-orphan", order_by="ResumeVersion.version.desc()")
    match_results = relationship("MatchResult", back_populates="resume",
                                 cascade="all, delete-orphan")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(String(36), primary_key=True, default=new_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    version = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    overall_score = Column(Float, nullable=True)
    section_scores = Column(JSON, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="versions")
