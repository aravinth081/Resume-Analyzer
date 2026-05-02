"""
Analytics API routes — skill gaps, trends, score history.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume, ResumeVersion, ResumeStatus

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/skills")
async def skill_gap_analysis(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze skill gaps across all user resumes vs. industry demand."""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == user.id, Resume.status == ResumeStatus.COMPLETED)
        .order_by(Resume.created_at.desc())
    )
    resumes = list(result.scalars().all())

    if not resumes:
        return {"message": "No analyzed resumes found", "skills": [], "gaps": []}

    # Aggregate all skills across resumes
    all_skills = set()
    for r in resumes:
        if r.skills:
            all_skills.update(s.lower() for s in r.skills)

    # Top in-demand skills for 2026
    in_demand = {
        "python", "javascript", "typescript", "react", "aws", "docker",
        "kubernetes", "sql", "git", "ci/cd", "machine learning",
        "rest api", "system design", "agile", "terraform"
    }

    current = {s for s in all_skills if s in in_demand}
    gaps = in_demand - all_skills

    return {
        "total_skills": len(all_skills),
        "current_skills": sorted(s.title() for s in all_skills),
        "in_demand_you_have": sorted(s.title() for s in current),
        "skill_gaps": sorted(s.title() for s in gaps),
        "coverage_percentage": round(len(current) / len(in_demand) * 100, 1),
    }


@router.get("/history")
async def score_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get resume score improvement history across versions."""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == user.id, Resume.status == ResumeStatus.COMPLETED)
        .order_by(Resume.created_at.asc())
    )
    resumes = list(result.scalars().all())

    history = []
    for r in resumes:
        history.append({
            "resume_id": str(r.id),
            "title": r.title,
            "version": r.version,
            "score": r.overall_score,
            "date": r.created_at.isoformat(),
        })

    return {
        "entries": history,
        "total_resumes": len(history),
        "best_score": max((h["score"] for h in history), default=0),
        "latest_score": history[-1]["score"] if history else 0,
        "improvement": (
            round(history[-1]["score"] - history[0]["score"], 1)
            if len(history) >= 2 else 0
        ),
    }


@router.get("/trends")
async def industry_trends(
    user: User = Depends(get_current_user),
):
    """Get industry trend insights (static data — in production, update from job board APIs)."""
    return {
        "trending_skills_2026": [
            {"skill": "AI/ML Engineering", "growth": "+45%", "demand": "very_high"},
            {"skill": "Cloud Architecture", "growth": "+32%", "demand": "high"},
            {"skill": "Kubernetes", "growth": "+28%", "demand": "high"},
            {"skill": "TypeScript", "growth": "+25%", "demand": "high"},
            {"skill": "Rust", "growth": "+40%", "demand": "moderate"},
            {"skill": "Data Engineering", "growth": "+35%", "demand": "very_high"},
            {"skill": "DevSecOps", "growth": "+30%", "demand": "high"},
            {"skill": "LLM/GenAI", "growth": "+60%", "demand": "very_high"},
        ],
        "salary_trends": {
            "software_engineer": {"median": "$135K", "growth": "+8%"},
            "data_scientist": {"median": "$145K", "growth": "+12%"},
            "ml_engineer": {"median": "$160K", "growth": "+15%"},
            "devops_engineer": {"median": "$140K", "growth": "+10%"},
        },
        "top_certifications": [
            "AWS Solutions Architect",
            "Google Cloud Professional",
            "Kubernetes Administrator (CKA)",
            "Terraform Associate",
            "Azure Data Engineer",
        ],
    }
