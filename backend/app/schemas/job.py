"""
Pydantic schemas for Job and Matching request/response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class JobCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    company: Optional[str] = None
    description: str = Field(..., min_length=50)
    experience_years: Optional[str] = None


class JobDetail(BaseModel):
    id: UUID
    title: str
    company: Optional[str] = None
    description: str
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_years: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    id: UUID
    title: str
    company: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    resume_id: UUID
    job_id: UUID


class MatchResponse(BaseModel):
    match_percentage: float
    matching_skills: List[str]
    missing_skills: List[str]
    role_suitability: str
    recommendations: List[str]


class RankRequest(BaseModel):
    job_id: UUID
    resume_ids: List[UUID] = Field(..., min_length=1, max_length=100)


class RankedCandidate(BaseModel):
    resume_id: UUID
    candidate_name: Optional[str] = None
    match_percentage: float
    matching_skills: List[str]
    missing_skills: List[str]
    overall_score: Optional[float] = None


class RankResponse(BaseModel):
    job_id: UUID
    job_title: str
    candidates: List[RankedCandidate]
    total_candidates: int
