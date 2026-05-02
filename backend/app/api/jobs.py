"""
Job Description & Matching API routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.job import (
    JobCreate, JobDetail, JobListItem,
    MatchRequest, MatchResponse, RankRequest, RankResponse
)
from app.services.matching_service import create_job_description, match_single, rank_candidates
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.job import JobDescription

router = APIRouter(tags=["Jobs & Matching"])


# ── Job Description Endpoints ──

@router.post("/jobs", response_model=JobDetail, status_code=201, tags=["Jobs"])
async def create_job(
    data: JobCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new job description with auto-extracted skills."""
    job = await create_job_description(
        title=data.title,
        company=data.company,
        description=data.description,
        experience_years=data.experience_years,
        user=user, db=db,
    )
    return job


@router.get("/jobs", response_model=List[JobListItem], tags=["Jobs"])
async def list_jobs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all job descriptions created by the user."""
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.user_id == user.id)
        .order_by(JobDescription.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/jobs/{job_id}", response_model=JobDetail, tags=["Jobs"])
async def get_job(
    job_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get job description details."""
    result = await db.execute(
        select(JobDescription).where(JobDescription.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ── Matching Endpoints ──

@router.post("/matching/match", response_model=MatchResponse, tags=["Matching"])
async def match_resume_job(
    data: MatchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Match a single resume against a job description."""
    return await match_single(data.resume_id, data.job_id, user, db)


@router.post("/matching/rank", response_model=RankResponse, tags=["Matching"])
async def rank(
    data: RankRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rank multiple candidates against a job description (Recruiter mode)."""
    return await rank_candidates(data.job_id, data.resume_ids, user, db)
