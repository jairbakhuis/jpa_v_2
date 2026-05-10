"""FastAPI entry point for JPA"""

import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from src.config import VPS_HOST, VPS_PORT, validate_config
from src.database.connection import init_db, test_connection
from src.integrations.telegram_bot import router as telegram_router
from src.integrations.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_config()

        # Initialize database
        logger.info("Initializing database...")
        init_db()

        # Test database connection
        if not test_connection():
            raise Exception("Database connection failed")

        # Start scheduler
        logger.info("Starting scheduler...")
        start_scheduler()

        logger.info("✓ JPA started successfully")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    yield

    # Shutdown
    try:
        logger.info("Shutting down...")
        stop_scheduler()
        logger.info("✓ JPA shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Create FastAPI app
app = FastAPI(
    title="JPA - Jair's Personal Assistant",
    description="AI-powered personal assistant with Telegram interface",
    version="1.0.0",
    lifespan=lifespan
)

# Register routers
app.include_router(telegram_router, prefix="/api", tags=["telegram"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "JPA",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "JPA - Jair's Personal Assistant",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "webhook": "/api/webhook",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting JPA on {VPS_HOST}:{VPS_PORT}")

    uvicorn.run(
        app,
        host=VPS_HOST,
        port=VPS_PORT,
        log_level="info"
    )
