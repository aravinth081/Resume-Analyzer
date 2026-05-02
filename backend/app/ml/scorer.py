"""
ATS (Applicant Tracking System) Scoring Algorithm.

Evaluates resumes on 5 weighted dimensions:
- Contact Info completeness (10%)
- Professional Summary quality (15%)
- Work Experience depth (30%)
- Skills relevance (25%)
- Education (10%)
- Formatting & structure (10%)

Each section is scored 0-100, then combined into a weighted overall score.
"""
from typing import Dict, List, Any, Optional
import re


def score_contact_info(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Score the completeness of contact information."""
    contact = parsed.get("contact", {})
    score = 0
    feedback_parts = []

    if contact.get("name"):
        score += 30
    else:
        feedback_parts.append("Add your full name")

    if contact.get("email"):
        score += 25
    else:
        feedback_parts.append("Include a professional email address")

    if contact.get("phone"):
        score += 20
    else:
        feedback_parts.append("Add a phone number")

    if contact.get("location"):
        score += 15
    else:
        feedback_parts.append("Include your city/location")

    if contact.get("linkedin"):
        score += 10
    else:
        feedback_parts.append("Add your LinkedIn profile URL")

    feedback = ". ".join(feedback_parts) if feedback_parts else "Complete contact information provided"
    return {"score": score, "feedback": feedback, "weight": 0.10}


def score_summary(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Score the professional summary section."""
    summary = parsed.get("summary", "")
    score = 0
    feedback_parts = []

    if not summary:
        return {
            "score": 0,
            "feedback": "Add a professional summary section highlighting key qualifications",
            "weight": 0.15
        }

    word_count = len(summary.split())

    # Length check (ideal: 50-150 words)
    if 50 <= word_count <= 150:
        score += 40
    elif 30 <= word_count < 50:
        score += 25
        feedback_parts.append("Expand your summary to 50-150 words")
    elif word_count > 150:
        score += 20
        feedback_parts.append("Shorten your summary to under 150 words")
    else:
        score += 10
        feedback_parts.append("Summary is too brief")

    # Check for quantifiable achievements
    if re.search(r'\d+[%+]|\$[\d,]+|\d+\s+years?', summary):
        score += 30
    else:
        feedback_parts.append("Include quantifiable achievements (e.g., '5+ years', '30% improvement')")

    # Check for action/power words
    power_words = ['led', 'developed', 'managed', 'created', 'designed',
                   'implemented', 'achieved', 'delivered', 'built', 'optimized']
    if any(w in summary.lower() for w in power_words):
        score += 30
    else:
        feedback_parts.append("Use strong action verbs to describe your impact")

    feedback = ". ".join(feedback_parts) if feedback_parts else "Strong professional summary"
    return {"score": min(100, score), "feedback": feedback, "weight": 0.15}


def score_experience(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Score work experience section — the most heavily weighted section."""
    experience = parsed.get("experience", [])
    score = 0
    feedback_parts = []

    if not experience:
        return {
            "score": 0,
            "feedback": "Add your work experience with detailed descriptions",
            "weight": 0.30
        }

    # Number of entries (ideal: 3-5)
    num_entries = len(experience)
    if 3 <= num_entries <= 5:
        score += 25
    elif 1 <= num_entries < 3:
        score += 15
        feedback_parts.append("Consider adding more relevant experience")
    elif num_entries > 5:
        score += 20
        feedback_parts.append("Focus on your 3-5 most relevant positions")

    # Check for job titles
    titled = sum(1 for e in experience if e.get("title"))
    if titled == num_entries:
        score += 15
    else:
        feedback_parts.append("Ensure all positions include a clear job title")

    # Check for date ranges
    dated = sum(1 for e in experience if e.get("dates"))
    if dated == num_entries:
        score += 15
    else:
        feedback_parts.append("Include date ranges for all positions")

    # Check descriptions for quality
    good_descriptions = 0
    for exp in experience:
        desc = exp.get("description", "")
        if len(desc.split()) >= 20:
            good_descriptions += 1
        # Check for metrics/numbers in description
        if re.search(r'\d+[%+]|\$[\d,]+', desc):
            score += 5  # Bonus for quantified achievements

    if good_descriptions >= num_entries * 0.7:
        score += 20
    else:
        feedback_parts.append("Add detailed bullet points describing your responsibilities and achievements")

    # Action verbs check
    all_desc = " ".join(e.get("description", "") for e in experience).lower()
    action_verbs = ['developed', 'managed', 'led', 'created', 'implemented',
                    'designed', 'improved', 'reduced', 'increased', 'delivered',
                    'built', 'launched', 'optimized', 'automated', 'mentored']
    verb_count = sum(1 for v in action_verbs if v in all_desc)
    if verb_count >= 5:
        score += 15
    elif verb_count >= 3:
        score += 10
    else:
        feedback_parts.append("Start bullet points with strong action verbs")

    feedback = ". ".join(feedback_parts) if feedback_parts else "Strong work experience section with quantified achievements"
    return {"score": min(100, score), "feedback": feedback, "weight": 0.30}


def score_skills(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Score the skills section."""
    skills = parsed.get("skills", [])
    score = 0
    feedback_parts = []

    if not skills:
        return {
            "score": 0,
            "feedback": "Add a dedicated skills section listing your technical and soft skills",
            "weight": 0.25
        }

    num_skills = len(skills)

    # Quantity (ideal: 8-20)
    if 8 <= num_skills <= 20:
        score += 40
    elif 5 <= num_skills < 8:
        score += 25
        feedback_parts.append("Add more relevant skills (aim for 8-20)")
    elif num_skills > 20:
        score += 30
        feedback_parts.append("Consider trimming to your top 15-20 most relevant skills")
    else:
        score += 15
        feedback_parts.append("Too few skills listed — expand your skills section")

    # Check for mix of technical and soft skills
    soft_skills = {'leadership', 'communication', 'teamwork', 'problem solving',
                   'project management', 'mentoring', 'strategic planning', 'agile', 'scrum'}
    tech_count = sum(1 for s in skills if s.lower() not in soft_skills)
    soft_count = sum(1 for s in skills if s.lower() in soft_skills)

    if tech_count >= 5 and soft_count >= 1:
        score += 30
    elif tech_count >= 3:
        score += 20
        feedback_parts.append("Include a few soft skills alongside technical skills")
    else:
        score += 10
        feedback_parts.append("Add more technical skills relevant to your target role")

    # In-demand skills bonus
    hot_skills = {'python', 'javascript', 'react', 'aws', 'docker', 'kubernetes',
                  'machine learning', 'data science', 'typescript', 'sql'}
    hot_count = sum(1 for s in skills if s.lower() in hot_skills)
    if hot_count >= 3:
        score += 30
    elif hot_count >= 1:
        score += 15
    else:
        feedback_parts.append("Consider adding in-demand skills like Python, React, AWS, or Docker")

    feedback = ". ".join(feedback_parts) if feedback_parts else "Well-rounded skills section with relevant technologies"
    return {"score": min(100, score), "feedback": feedback, "weight": 0.25}


def score_education(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Score the education section."""
    education = parsed.get("education", [])
    score = 0
    feedback_parts = []

    if not education:
        return {
            "score": 20,
            "feedback": "Add your educational qualifications",
            "weight": 0.10
        }

    # Has at least one degree
    score += 40

    # Check for institution names
    if any(e.get("institution") for e in education):
        score += 20
    else:
        feedback_parts.append("Include institution names")

    # Check for graduation year
    if any(e.get("year") for e in education):
        score += 20
    else:
        feedback_parts.append("Include graduation years")

    # GPA (if good)
    if any(e.get("gpa") for e in education):
        score += 20
    else:
        score += 10  # Partial credit — GPA is optional

    feedback = ". ".join(feedback_parts) if feedback_parts else "Well-structured education section"
    return {"score": min(100, score), "feedback": feedback, "weight": 0.10}


def score_formatting(raw_text: str) -> Dict[str, Any]:
    """Score the overall formatting and structure of the resume."""
    score = 0
    feedback_parts = []

    if not raw_text:
        return {"score": 0, "feedback": "Unable to evaluate formatting", "weight": 0.10}

    word_count = len(raw_text.split())
    line_count = len(raw_text.split('\n'))

    # Length check (ideal: 400-800 words for 1-page, up to 1200 for 2-page)
    if 400 <= word_count <= 1200:
        score += 30
    elif 300 <= word_count < 400:
        score += 20
        feedback_parts.append("Resume is slightly short — aim for 400-800 words")
    elif word_count > 1200:
        score += 15
        feedback_parts.append("Resume may be too long — consider condensing to 1-2 pages")
    else:
        score += 10
        feedback_parts.append("Resume is too brief — add more content")

    # Section structure (check for distinct sections)
    section_keywords = ['experience', 'education', 'skills', 'summary', 'objective', 'projects']
    sections_found = sum(1 for kw in section_keywords
                         if re.search(rf'\b{kw}\b', raw_text.lower()))
    if sections_found >= 4:
        score += 30
    elif sections_found >= 2:
        score += 20
        feedback_parts.append("Add more clearly labeled sections")
    else:
        score += 5
        feedback_parts.append("Organize resume into clear sections (Experience, Education, Skills)")

    # Bullet points usage
    bullet_count = raw_text.count('•') + raw_text.count('-') + raw_text.count('*')
    if bullet_count >= 5:
        score += 20
    else:
        feedback_parts.append("Use bullet points to make content more scannable")

    # Consistent formatting (line length variation)
    lines = [l for l in raw_text.split('\n') if l.strip()]
    if len(lines) >= 10:
        score += 20
    else:
        feedback_parts.append("Add more detailed content across sections")

    feedback = ". ".join(feedback_parts) if feedback_parts else "Good resume structure and formatting"
    return {"score": min(100, score), "feedback": feedback, "weight": 0.10}


def calculate_ats_score(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master scoring function — calculates the complete ATS score.

    Returns:
        {
            "overall_score": float (0-100),
            "sections": { section_name: { score, feedback, weight } },
            "suggestions": [ improvement recommendations ]
        }
    """
    raw_text = parsed_data.get("raw_text", "")

    sections = {
        "contact_info": score_contact_info(parsed_data),
        "summary": score_summary(parsed_data),
        "experience": score_experience(parsed_data),
        "skills": score_skills(parsed_data),
        "education": score_education(parsed_data),
        "formatting": score_formatting(raw_text),
    }

    # Weighted overall score
    overall = sum(s["score"] * s["weight"] for s in sections.values())

    # Generate prioritized suggestions
    suggestions = []
    # Sort sections by score (lowest first) to prioritize worst areas
    sorted_sections = sorted(sections.items(), key=lambda x: x[1]["score"])

    for name, data in sorted_sections:
        if data["score"] < 80 and data["feedback"]:
            suggestions.append(f"[{name.replace('_', ' ').title()}] {data['feedback']}")

    # Add general suggestions
    if overall < 50:
        suggestions.insert(0, "Your resume needs significant improvements — focus on the lowest-scoring sections first")
    elif overall < 70:
        suggestions.insert(0, "Good foundation — address the specific feedback below to reach a competitive score")

    return {
        "overall_score": round(overall, 1),
        "sections": sections,
        "suggestions": suggestions[:8],  # Cap at 8 actionable suggestions
    }
