"""
FastAPI Application Entry Point.

Configures middleware, CORS, lifespan events, and routes.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.config import settings
from app.database import async_engine, Base
from app.api.auth import router as auth_router
from app.api.resumes import router as resume_router
from app.api.jobs import router as jobs_router
from app.api.chat import router as chat_router
from app.api.analytics import router as analytics_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — initialize and cleanup resources."""
    logger.info("🚀 Starting AI Resume Intelligence Platform...")

    # Create database tables (use Alembic migrations in production)
    async with async_engine.begin() as conn:
        # Import all models to register them with Base
        from app.models import (
            User, Tenant, Subscription, ChatMessage,
            Resume, ResumeVersion, JobDescription, MatchResult
        )
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ Database tables ready")
    logger.info(f"📊 App: {settings.APP_NAME} v{settings.APP_VERSION}")

    yield

    # Cleanup
    await async_engine.dispose()
    logger.info("👋 Application shutdown complete")


# ── Create FastAPI App ──
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered resume analysis, ATS scoring, and semantic job matching platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing middleware ──
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# ── Global exception handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."}
    )


# ── Register Routers ──
API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(resume_router, prefix=API_PREFIX)
app.include_router(jobs_router, prefix=API_PREFIX)
app.include_router(chat_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)


# ── Health Check ──
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }
