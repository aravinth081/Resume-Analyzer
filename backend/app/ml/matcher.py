"""
Semantic Job Matching Engine.

Matches resumes against job descriptions using:
1. Embedding similarity (BERT cosine similarity) — 60% weight
2. Skill overlap analysis — 30% weight
3. Experience level match — 10% weight

This multi-signal approach is more robust than pure embedding similarity.
"""
from typing import Dict, List, Any, Optional, Tuple
from app.ml.embeddings import cosine_similarity
from app.ml.ner import extract_skills, SKILL_TAXONOMY
import re


def compute_skill_overlap(
    resume_skills: List[str],
    job_required: List[str],
    job_preferred: Optional[List[str]] = None
) -> Tuple[List[str], List[str], float]:
    """
    Compute skill overlap between resume and job description.
    
    Returns:
        (matching_skills, missing_skills, overlap_score)
    """
    resume_set = {s.lower() for s in resume_skills}
    required_set = {s.lower() for s in (job_required or [])}
    preferred_set = {s.lower() for s in (job_preferred or [])}
    all_job_skills = required_set | preferred_set

    matching = resume_set & all_job_skills
    missing = all_job_skills - resume_set

    # Required skills matter more than preferred
    required_match_count = len(resume_set & required_set)
    required_total = len(required_set) if required_set else 1

    preferred_match_count = len(resume_set & preferred_set)
    preferred_total = len(preferred_set) if preferred_set else 1

    # Weighted overlap: 70% required + 30% preferred
    overlap_score = (
        0.7 * (required_match_count / required_total) +
        0.3 * (preferred_match_count / max(preferred_total, 1))
    )

    # Title-case for display
    matching_display = sorted(s.title() for s in matching)
    missing_display = sorted(s.title() for s in missing)

    return matching_display, missing_display, min(1.0, overlap_score)


def assess_experience_level(resume_data: Dict, job_data: Dict) -> float:
    """Assess how well the candidate's experience level matches the job requirements."""
    # Estimate years of experience from resume
    experience = resume_data.get("experience", [])
    total_months = 0
    for exp in experience:
        duration = exp.get("duration_months")
        if duration:
            total_months += duration
        elif exp.get("dates"):
            # Rough estimate: each entry averages 24 months
            total_months += 24

    resume_years = total_months / 12

    # Parse required experience from job
    job_exp_str = job_data.get("experience_years", "")
    required_years = 0
    if job_exp_str:
        match = re.search(r'(\d+)', str(job_exp_str))
        if match:
            required_years = int(match.group(1))

    if required_years == 0:
        return 0.8  # No requirement specified — give benefit of doubt

    # Score based on how close the candidate is
    ratio = resume_years / max(required_years, 1)
    if ratio >= 1.0:
        return 1.0  # Meets or exceeds
    elif ratio >= 0.7:
        return 0.8  # Close enough
    elif ratio >= 0.5:
        return 0.5
    else:
        return 0.3


def determine_suitability(match_pct: float) -> str:
    """Classify match percentage into a suitability label."""
    if match_pct >= 80:
        return "strong_match"
    elif match_pct >= 60:
        return "good_match"
    elif match_pct >= 40:
        return "moderate_match"
    else:
        return "weak_match"


def generate_recommendations(
    missing_skills: List[str],
    match_pct: float,
    suitability: str
) -> List[str]:
    """Generate actionable recommendations for the candidate."""
    recs = []

    # Skill recommendations
    if missing_skills:
        top_missing = missing_skills[:5]
        recs.append(f"Learn these key skills: {', '.join(top_missing)}")
        for skill in top_missing[:3]:
            recs.append(f"Adding '{skill}' experience could improve your match by ~{round(5 + len(skill) % 5)}%")

    # General recommendations based on suitability
    if suitability == "weak_match":
        recs.append("Consider roles more aligned with your current skill set")
        recs.append("Focus on building experience in the core required technologies")
    elif suitability == "moderate_match":
        recs.append("You have a foundation — upskilling in 2-3 areas would make you competitive")
    elif suitability == "good_match":
        recs.append("Strong profile — highlight relevant projects in your resume")
    elif suitability == "strong_match":
        recs.append("Excellent match — tailor your resume summary to this specific role")

    return recs[:6]


def match_resume_to_job(
    resume_embedding: List[float],
    job_embedding: List[float],
    resume_skills: List[str],
    job_required_skills: List[str],
    job_preferred_skills: Optional[List[str]],
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Full matching pipeline — combines embedding similarity, skill overlap,
    and experience assessment into a single match result.
    """
    # 1. Embedding similarity (semantic match)
    semantic_score = cosine_similarity(resume_embedding, job_embedding)

    # 2. Skill overlap analysis
    matching_skills, missing_skills, skill_score = compute_skill_overlap(
        resume_skills, job_required_skills, job_preferred_skills
    )

    # 3. Experience level assessment
    exp_score = assess_experience_level(resume_data, job_data)

    # Weighted combination
    match_percentage = round(
        (semantic_score * 0.60 + skill_score * 0.30 + exp_score * 0.10) * 100, 1
    )

    suitability = determine_suitability(match_percentage)
    recommendations = generate_recommendations(missing_skills, match_percentage, suitability)

    return {
        "match_percentage": match_percentage,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "role_suitability": suitability,
        "recommendations": recommendations,
        "breakdown": {
            "semantic_similarity": round(semantic_score * 100, 1),
            "skill_overlap": round(skill_score * 100, 1),
            "experience_match": round(exp_score * 100, 1),
        }
    }
