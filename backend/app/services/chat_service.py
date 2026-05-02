"""
AI Career Copilot chat service.
Uses context from user's resume data to provide personalized career advice.
Implements a rule-based + template approach (can be upgraded to LLM API).
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.user import User, ChatMessage
from app.models.resume import Resume, ResumeStatus


# ── Knowledge base for career advice ──
CAREER_ADVICE = {
    "improve_resume": [
        "Start each bullet point with a strong action verb (e.g., 'Developed', 'Led', 'Optimized')",
        "Quantify your achievements with numbers and percentages",
        "Tailor your resume to each specific job description",
        "Keep your resume to 1-2 pages maximum",
        "Include a compelling professional summary at the top",
        "Use industry-standard section headings",
        "Remove outdated or irrelevant experience",
    ],
    "skills_to_learn": {
        "software_engineering": ["Kubernetes", "System Design", "CI/CD", "Cloud Architecture", "Microservices"],
        "data_science": ["MLOps", "Deep Learning", "Feature Engineering", "A/B Testing", "Data Pipelines"],
        "web_development": ["TypeScript", "Next.js", "GraphQL", "Docker", "Performance Optimization"],
        "general": ["Git", "Agile/Scrum", "Communication", "Problem Solving", "API Design"],
    },
    "interview_tips": [
        "Research the company thoroughly before the interview",
        "Prepare STAR-method stories for behavioral questions",
        "Practice common technical questions for your field",
        "Ask thoughtful questions about the role and team",
        "Follow up with a thank-you email within 24 hours",
    ],
}


def detect_intent(message: str) -> str:
    """Detect user intent from the message."""
    msg = message.lower()

    if any(kw in msg for kw in ["improve", "better", "fix", "enhance", "update"]):
        return "improve_resume"
    elif any(kw in msg for kw in ["skill", "learn", "study", "course", "trending"]):
        return "skills_to_learn"
    elif any(kw in msg for kw in ["interview", "prepare", "question"]):
        return "interview_tips"
    elif any(kw in msg for kw in ["score", "ats", "rating"]):
        return "score_analysis"
    elif any(kw in msg for kw in ["match", "job", "fit", "suitable"]):
        return "job_matching"
    elif any(kw in msg for kw in ["gap", "missing", "lack"]):
        return "skill_gap"
    else:
        return "general"


def generate_response(
    intent: str,
    message: str,
    resume_context: Optional[Dict[str, Any]] = None
) -> str:
    """Generate a contextual response based on intent and resume data."""

    if intent == "improve_resume":
        tips = CAREER_ADVICE["improve_resume"]
        response = "Here are my top recommendations to improve your resume:\n\n"
        for i, tip in enumerate(tips[:5], 1):
            response += f"{i}. {tip}\n"

        if resume_context:
            score = resume_context.get("overall_score")
            suggestions = resume_context.get("suggestions", [])
            if score:
                response += f"\n📊 Your current ATS score is **{score}/100**.\n\n"
            if suggestions:
                response += "Based on your resume analysis, focus on:\n"
                for s in suggestions[:3]:
                    response += f"• {s}\n"
        return response

    elif intent == "skills_to_learn":
        skills = resume_context.get("skills", []) if resume_context else []
        skill_lower = [s.lower() for s in skills]

        # Determine domain from existing skills
        if any(s in skill_lower for s in ["python", "machine learning", "tensorflow", "pytorch"]):
            domain = "data_science"
        elif any(s in skill_lower for s in ["react", "javascript", "html", "css", "vue"]):
            domain = "web_development"
        elif any(s in skill_lower for s in ["java", "docker", "aws", "kubernetes"]):
            domain = "software_engineering"
        else:
            domain = "general"

        rec_skills = CAREER_ADVICE["skills_to_learn"][domain]
        # Filter out skills they already have
        new_skills = [s for s in rec_skills if s.lower() not in skill_lower]

        response = f"Based on your profile ({domain.replace('_', ' ').title()}), I recommend learning:\n\n"
        for i, skill in enumerate(new_skills[:5], 1):
            response += f"{i}. **{skill}** — highly in-demand for 2026\n"

        if skills:
            response += f"\n✅ You already have strong skills in: {', '.join(skills[:5])}"
        return response

    elif intent == "interview_tips":
        tips = CAREER_ADVICE["interview_tips"]
        response = "Here are key interview preparation tips:\n\n"
        for i, tip in enumerate(tips, 1):
            response += f"{i}. {tip}\n"
        return response

    elif intent == "score_analysis":
        if resume_context:
            score = resume_context.get("overall_score", "N/A")
            sections = resume_context.get("section_scores", {})
            response = f"📊 **Your ATS Score: {score}/100**\n\n"
            if sections:
                response += "Section Breakdown:\n"
                for name, data in sections.items():
                    if isinstance(data, dict):
                        s = data.get("score", "N/A")
                        response += f"• {name.replace('_', ' ').title()}: {s}/100\n"
            return response
        return "Upload a resume first so I can analyze your ATS score!"

    elif intent == "skill_gap":
        if resume_context:
            skills = resume_context.get("skills", [])
            response = "Here's your skill gap analysis:\n\n"
            response += f"**Current Skills ({len(skills)}):** {', '.join(skills[:10])}\n\n"
            # Suggest commonly paired skills they're missing
            all_hot = {"Python", "JavaScript", "React", "AWS", "Docker", "SQL",
                       "Git", "REST API", "CI/CD", "Kubernetes"}
            missing = all_hot - {s.title() for s in skills}
            if missing:
                response += f"**Recommended to Add:** {', '.join(list(missing)[:5])}\n"
            return response
        return "Upload your resume to get a personalized skill gap analysis!"

    else:
        response = ("I'm your AI Career Copilot! I can help you with:\n\n"
                     "🔹 **Improving your resume** — just ask 'How to improve my resume?'\n"
                     "🔹 **Skills to learn** — ask 'What skills should I learn?'\n"
                     "🔹 **Interview prep** — ask 'How to prepare for interviews?'\n"
                     "🔹 **Score analysis** — ask 'What is my ATS score?'\n"
                     "🔹 **Skill gaps** — ask 'What skills am I missing?'\n\n"
                     "Try asking me something!")
        return response


async def chat(
    message: str, user: User, db: AsyncSession
) -> Dict[str, str]:
    """Process a chat message and return AI response."""
    # Get latest resume context
    res = await db.execute(
        select(Resume)
        .where(Resume.user_id == user.id, Resume.status == ResumeStatus.COMPLETED)
        .order_by(Resume.created_at.desc())
        .limit(1)
    )
    latest_resume = res.scalar_one_or_none()

    resume_context = None
    if latest_resume:
        resume_context = {
            "skills": latest_resume.skills or [],
            "overall_score": latest_resume.overall_score,
            "section_scores": latest_resume.section_scores,
            "suggestions": latest_resume.suggestions,
            "parsed_data": latest_resume.parsed_data,
        }

    # Detect intent and generate response
    intent = detect_intent(message)
    response = generate_response(intent, message, resume_context)

    # Save messages to history
    user_msg = ChatMessage(user_id=user.id, role="user", content=message)
    assistant_msg = ChatMessage(user_id=user.id, role="assistant", content=response)
    db.add(user_msg)
    db.add(assistant_msg)
    await db.flush()

    return {"role": "assistant", "content": response}


async def get_chat_history(
    user: User, db: AsyncSession, limit: int = 50
) -> List[Dict[str, str]]:
    """Get recent chat history for a user."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()  # Chronological order

    return [{"role": m.role, "content": m.content, "timestamp": m.created_at.isoformat()}
            for m in messages]
