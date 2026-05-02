"""
Resume API routes — upload, list, detail, score, delete.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.resume import (
    ResumeUploadResponse, ResumeDetail, ResumeListItem, ResumeScoreResponse
)
from app.services.resume_service import (
    upload_resume, process_resume, get_user_resumes, get_resume_by_id, delete_resume
)
from app.core.dependencies import get_current_user, check_upload_limit
from app.models.user import User
from app.models.resume import ResumeStatus

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=202)
async def upload(
    file: UploadFile = File(...),
    title: str = Form(default="Untitled Resume"),
    user: User = Depends(check_upload_limit),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a resume (PDF/DOCX) for analysis.
    The resume will be processed asynchronously.
    """
    resume = await upload_resume(file, title, user, db)

    # Process inline for now (in production, use Celery task)
    # from app.tasks.resume_tasks import process_resume_task
    # process_resume_task.delay(str(resume.id))
    await process_resume(resume.id, db)

    return ResumeUploadResponse(
        id=resume.id,
        status=resume.status,
        message="Resume uploaded and analyzed successfully",
        estimated_time_seconds=0,
    )


@router.get("", response_model=List[ResumeListItem])
async def list_resumes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all resumes for the current user."""
    resumes = await get_user_resumes(user, db)
    return resumes


@router.get("/{resume_id}", response_model=ResumeDetail)
async def get_resume(
    resume_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed resume information including parsed data."""
    return await get_resume_by_id(resume_id, user, db)


@router.get("/{resume_id}/score", response_model=ResumeScoreResponse)
async def get_score(
    resume_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ATS score breakdown for a resume."""
    resume = await get_resume_by_id(resume_id, user, db)
    if resume.status != ResumeStatus.COMPLETED:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Resume is still processing")

    return ResumeScoreResponse(
        resume_id=resume.id,
        overall_score=resume.overall_score or 0,
        sections=resume.section_scores or {},
        suggestions=resume.suggestions or [],
    )


@router.delete("/{resume_id}", status_code=204)
async def remove_resume(
    resume_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a resume."""
    await delete_resume(resume_id, user, db)
