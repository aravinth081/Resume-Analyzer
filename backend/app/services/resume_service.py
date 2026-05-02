"""
Resume service — handles upload, retrieval, and processing orchestration.
"""
import os
import uuid
import shutil
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.resume import Resume, ResumeVersion, ResumeStatus
from app.models.user import User, Subscription
from app.config import settings
from app.ml.parser import parse_resume_file, clean_text
from app.ml.ner import extract_all
from app.ml.embeddings import generate_embedding
from app.ml.scorer import calculate_ats_score


async def upload_resume(
    file: UploadFile,
    title: str,
    user: User,
    db: AsyncSession,
) -> Resume:
    """
    Handle resume upload:
    1. Validate file type and size
    2. Save to disk
    3. Create DB record
    4. Increment usage counter
    """
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Generate unique filename and save
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

    # Read file content and check size
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    # Create resume record
    resume = Resume(
        user_id=user.id,
        tenant_id=user.tenant_id,
        title=title,
        file_path=file_path,
        file_type=ext.lstrip('.'),
        status=ResumeStatus.UPLOADED,
    )
    db.add(resume)

    # Increment upload counter
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = sub_result.scalar_one_or_none()
    if sub:
        sub.resumes_uploaded_this_month += 1

    await db.flush()
    return resume


async def process_resume(resume_id: UUID, db: AsyncSession) -> Resume:
    """
    Full resume processing pipeline (called by Celery worker or inline):
    1. Parse file → extract text
    2. Run NER → extract structured data
    3. Generate embeddings
    4. Calculate ATS score
    5. Store results
    """
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume.status = ResumeStatus.PROCESSING
    await db.flush()

    try:
        # Step 1: Parse file
        raw_text = parse_resume_file(resume.file_path)
        cleaned_text = clean_text(raw_text)

        # Step 2: NER extraction
        parsed_data = extract_all(cleaned_text)
        resume.parsed_data = parsed_data
        resume.skills = parsed_data.get("skills", [])

        # Step 3: Generate embedding
        embedding = generate_embedding(cleaned_text)
        resume.embedding = embedding

        # Step 4: ATS scoring
        score_result = calculate_ats_score(parsed_data)
        resume.overall_score = score_result["overall_score"]
        resume.section_scores = score_result["sections"]
        resume.suggestions = score_result["suggestions"]

        # Step 5: Create version snapshot
        version = ResumeVersion(
            resume_id=resume.id,
            version=resume.version,
            file_path=resume.file_path,
            overall_score=resume.overall_score,
            section_scores=resume.section_scores,
            parsed_data=resume.parsed_data,
        )
        db.add(version)

        resume.status = ResumeStatus.COMPLETED
        await db.flush()

    except Exception as e:
        resume.status = ResumeStatus.FAILED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process resume: {str(e)}"
        )

    return resume


async def get_user_resumes(user: User, db: AsyncSession) -> List[Resume]:
    """Get all resumes for a user."""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == user.id)
        .order_by(Resume.created_at.desc())
    )
    return list(result.scalars().all())


async def get_resume_by_id(resume_id: UUID, user: User, db: AsyncSession) -> Resume:
    """Get a specific resume, ensuring ownership."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


async def delete_resume(resume_id: UUID, user: User, db: AsyncSession) -> None:
    """Delete a resume and its file."""
    resume = await get_resume_by_id(resume_id, user, db)
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    await db.delete(resume)
    await db.flush()
