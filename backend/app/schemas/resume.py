"""
Pydantic schemas for Resume request/response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.resume import ResumeStatus


class ResumeUploadResponse(BaseModel):
    id: UUID
    status: ResumeStatus
    message: str
    estimated_time_seconds: int = 15


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None


class ExperienceEntry(BaseModel):
    title: str
    company: str
    dates: Optional[str] = None
    description: Optional[str] = None
    duration_months: Optional[int] = None


class EducationEntry(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None
    gpa: Optional[str] = None


class ParsedResumeData(BaseModel):
    contact: Optional[ContactInfo] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[ExperienceEntry] = []
    education: List[EducationEntry] = []
    certifications: List[str] = []


class SectionScore(BaseModel):
    score: float
    feedback: str
    weight: float


class ResumeScoreResponse(BaseModel):
    resume_id: UUID
    overall_score: float
    sections: Dict[str, SectionScore]
    suggestions: List[str]


class ResumeDetail(BaseModel):
    id: UUID
    title: str
    status: ResumeStatus
    version: int
    file_type: str
    parsed_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    overall_score: Optional[float] = None
    section_scores: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeListItem(BaseModel):
    id: UUID
    title: str
    status: ResumeStatus
    version: int
    overall_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeVersionItem(BaseModel):
    id: UUID
    version: int
    overall_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
