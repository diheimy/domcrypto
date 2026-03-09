"""Database connection and session management.

Following BACKEND-SPEC.md specification for PostgreSQL + SQLAlchemy.
"""

import logging
from typing import Optional, Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.backend.config.settings import DATABASE_URL

logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,  # Use StaticPool for SQLite, QueuePool for PostgreSQL
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max overflow connections
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """Get database session.

    Usage as dependency:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions.

    Usage:
        with db_session() as db:
            # do something with db
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db() -> None:
    """Initialize database tables."""
    from src.backend.models import Base

    logger.info("📊 Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


def drop_db() -> None:
    """Drop all database tables."""
    from src.backend.models import Base

    logger.warning("⚠️ Dropping all database tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped")
    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        raise


# =============================================================================
# HEALTH CHECK
# =============================================================================

def check_db_health() -> bool:
    """Check database connection health."""
    try:
        with db_session() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
