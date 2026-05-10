"""Configuration loader for JPA"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
load_dotenv(Path("/home/jpa/.jpa/.env"), override=True)

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jpa_user:password@localhost/jpa_db")

# Gmail
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "/home/jpa/.jpa/gmail_credentials.json")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "/home/jpa/.jpa/gmail_token.json")

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# VPS
VPS_HOST = os.getenv("VPS_HOST", "0.0.0.0")
VPS_PORT = int(os.getenv("VPS_PORT", "8000"))
TIMEZONE = os.getenv("TIMEZONE", "America/Curacao")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validate critical configs
def validate_config():
    """Validate that all required configs are set"""
    required = [
        ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
        ("TELEGRAM_TOKEN", TELEGRAM_TOKEN),
        ("TELEGRAM_USER_ID", TELEGRAM_USER_ID),
        ("DATABASE_URL", DATABASE_URL),
    ]

    missing = [name for name, value in required if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
