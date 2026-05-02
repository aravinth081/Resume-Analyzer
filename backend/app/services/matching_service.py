"""
Matching service — handles resume-to-job matching and candidate ranking.
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from fastapi import HTTPException

from app.models.resume import Resume, ResumeStatus
from app.models.job import JobDescription, MatchResult
from app.models.user import User
from app.ml.embeddings import generate_embedding, cosine_similarity
from app.ml.ner import extract_skills
from app.ml.matcher import match_resume_to_job


async def create_job_description(
    title: str, company: str, description: str,
    experience_years: str, user: User, db: AsyncSession
) -> JobDescription:
    """Create a job description with extracted skills and embedding."""
    # Extract skills from JD text
    required_skills = extract_skills(description)

    # Generate embedding
    embedding = generate_embedding(description)

    job = JobDescription(
        user_id=user.id,
        tenant_id=user.tenant_id,
        title=title,
        company=company,
        description=description,
        required_skills=required_skills,
        preferred_skills=[],
        experience_years=experience_years,
        embedding=embedding,
    )
    db.add(job)
    await db.flush()
    return job


async def match_single(
    resume_id: UUID, job_id: UUID, user: User, db: AsyncSession
) -> Dict[str, Any]:
    """Match a single resume against a single job description."""
    # Fetch resume
    res = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = res.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.status != ResumeStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Resume is still processing")

    # Fetch job
    job_res = await db.execute(select(JobDescription).where(JobDescription.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    # Run matching
    result = match_resume_to_job(
        resume_embedding=resume.embedding,
        job_embedding=job.embedding,
        resume_skills=resume.skills or [],
        job_required_skills=job.required_skills or [],
        job_preferred_skills=job.preferred_skills,
        resume_data=resume.parsed_data or {},
        job_data={"experience_years": job.experience_years},
    )

    # Save match result
    match_record = MatchResult(
        resume_id=resume.id,
        job_id=job.id,
        tenant_id=user.tenant_id,
        match_percentage=result["match_percentage"],
        matching_skills=result["matching_skills"],
        missing_skills=result["missing_skills"],
        role_suitability=result["role_suitability"],
        recommendations=result["recommendations"],
    )
    db.add(match_record)
    await db.flush()

    return result


async def rank_candidates(
    job_id: UUID, resume_ids: List[UUID], user: User, db: AsyncSession
) -> Dict[str, Any]:
    """Rank multiple candidates against a job description."""
    # Fetch job
    job_res = await db.execute(select(JobDescription).where(JobDescription.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    # Fetch all resumes
    res = await db.execute(
        select(Resume).where(
            Resume.id.in_(resume_ids),
            Resume.status == ResumeStatus.COMPLETED
        )
    )
    resumes = list(res.scalars().all())

    if not resumes:
        raise HTTPException(status_code=404, detail="No completed resumes found")

    # Match each resume
    candidates = []
    for resume in resumes:
        result = match_resume_to_job(
            resume_embedding=resume.embedding,
            job_embedding=job.embedding,
            resume_skills=resume.skills or [],
            job_required_skills=job.required_skills or [],
            job_preferred_skills=job.preferred_skills,
            resume_data=resume.parsed_data or {},
            job_data={"experience_years": job.experience_years},
        )
        contact = (resume.parsed_data or {}).get("contact", {})
        candidates.append({
            "resume_id": str(resume.id),
            "candidate_name": contact.get("name", "Unknown"),
            "match_percentage": result["match_percentage"],
            "matching_skills": result["matching_skills"],
            "missing_skills": result["missing_skills"],
            "overall_score": resume.overall_score,
        })

    # Sort by match percentage descending
    candidates.sort(key=lambda c: c["match_percentage"], reverse=True)

    return {
        "job_id": str(job.id),
        "job_title": job.title,
        "candidates": candidates,
        "total_candidates": len(candidates),
    }
