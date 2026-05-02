"""
Async database engine and session management using SQLAlchemy 2.0.
Supports both SQLite (dev) and PostgreSQL (production).
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine, event
from app.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# ── Async Engine (for FastAPI) ──
engine_kwargs = {
    "echo": settings.DEBUG,
}
if not is_sqlite:
    engine_kwargs.update(pool_size=20, max_overflow=10, pool_pre_ping=True)

async_engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── Sync Engine (for Celery workers + Alembic) ──
sync_kwargs = {"echo": settings.DEBUG}
if not is_sqlite:
    sync_kwargs.update(pool_size=10, max_overflow=5, pool_pre_ping=True)

sync_engine = create_engine(settings.DATABASE_SYNC_URL, **sync_kwargs)

SyncSessionLocal = sessionmaker(bind=sync_engine)


# ── Base Model ──
class Base(DeclarativeBase):
    pass


# ── Enable WAL mode and foreign keys for SQLite ──
if is_sqlite:
    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ── Dependency: get async DB session ──
async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
