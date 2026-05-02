"""
SQLAlchemy ORM models — Job Descriptions and Match Results.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, DateTime, Float, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

def new_uuid():
    return str(uuid.uuid4())

class JobDescription(Base):
    """
    Job description entity. Stores the JD text and its computed embedding
    for semantic matching against candidate resumes.
    """
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    tenant_id = Column(String(36), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=True)   # Extracted required skills
    preferred_skills = Column(JSON, nullable=True)   # Nice-to-have skills
    experience_years = Column(String(50), nullable=True)
    embedding = Column(JSON, nullable=True)          # Sentence embedding vector

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    match_results = relationship("MatchResult", back_populates="job",
                                 cascade="all, delete-orphan")


class MatchResult(Base):
    """
    Stores the result of matching a resume against a job description.
    Includes the similarity score, skill analysis, and recommendations.
    """
    __tablename__ = "match_results"

    id = Column(String(36), primary_key=True, default=new_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"),
                    nullable=False, index=True)
    tenant_id = Column(String(36), nullable=True, index=True)

    match_percentage = Column(Float, nullable=False)
    matching_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    role_suitability = Column(String(50), nullable=True)  # strong_match, moderate, weak
    recommendations = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="match_results")
    job = relationship("JobDescription", back_populates="match_results")
