"""
Celery background tasks for resume processing.

These tasks run asynchronously via the Celery worker so that
heavy ML operations don't block the API response.
"""
from celery import Celery
from app.config import settings

# ── Celery App ──
celery_app = Celery(
    "resume_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minute hard limit
    task_soft_time_limit=240,  # 4 minute soft limit
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_resume_task(self, resume_id: str):
    """
    Background task to process a resume through the full ML pipeline.
    
    This runs in a Celery worker process using a synchronous DB session
    since Celery doesn't support async natively.
    """
    from app.database import SyncSessionLocal
    from app.models.resume import Resume, ResumeVersion, ResumeStatus
    from app.ml.parser import parse_resume_file, clean_text
    from app.ml.ner import extract_all
    from app.ml.embeddings import generate_embedding
    from app.ml.scorer import calculate_ats_score
    from uuid import UUID

    session = SyncSessionLocal()
    try:
        resume = session.query(Resume).filter(Resume.id == UUID(resume_id)).first()
        if not resume:
            return {"error": "Resume not found"}

        resume.status = ResumeStatus.PROCESSING
        session.commit()

        # Step 1: Parse
        raw_text = parse_resume_file(resume.file_path)
        cleaned_text = clean_text(raw_text)

        # Step 2: NER
        parsed_data = extract_all(cleaned_text)
        resume.parsed_data = parsed_data
        resume.skills = parsed_data.get("skills", [])

        # Step 3: Embeddings
        embedding = generate_embedding(cleaned_text)
        resume.embedding = embedding

        # Step 4: Score
        score_result = calculate_ats_score(parsed_data)
        resume.overall_score = score_result["overall_score"]
        resume.section_scores = score_result["sections"]
        resume.suggestions = score_result["suggestions"]

        # Step 5: Version snapshot
        version = ResumeVersion(
            resume_id=resume.id,
            version=resume.version,
            file_path=resume.file_path,
            overall_score=resume.overall_score,
            section_scores=resume.section_scores,
            parsed_data=resume.parsed_data,
        )
        session.add(version)

        resume.status = ResumeStatus.COMPLETED
        session.commit()

        return {
            "resume_id": resume_id,
            "status": "completed",
            "score": resume.overall_score,
        }

    except Exception as exc:
        session.rollback()
        resume.status = ResumeStatus.FAILED
        session.commit()
        # Retry on transient failures
        self.retry(exc=exc)

    finally:
        session.close()
