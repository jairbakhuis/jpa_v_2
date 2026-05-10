"""PostgreSQL connection and session management"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections every hour
        echo=False           # Set to True for SQL debugging
    )
    logger.info("✓ PostgreSQL engine created")
except Exception as e:
    logger.error(f"Failed to create engine: {e}")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        from src.database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables initialized")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {e}")
        raise

def test_connection():
    """Test database connection"""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
