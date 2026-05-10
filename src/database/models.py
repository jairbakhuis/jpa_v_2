"""SQLAlchemy models for JPA"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    """Store conversation history"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, default={})

class Memory(Base):
    """Store extracted facts and memories"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    fact = Column(Text, nullable=False)  # e.g., "Anke is Jair's wife"
    category = Column(String(50), nullable=False)  # e.g., "family", "work", "interests"
    confidence = Column(Integer, default=100)  # 0-100 confidence score
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source = Column(String(255))  # Where this fact came from (conversation ID, etc.)

class Task(Base):
    """Store tasks and reminders"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    due_time = Column(String(5))  # HH:MM format
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmailCache(Base):
    """Cache of recently processed emails"""
    __tablename__ = "email_cache"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    email_id = Column(String(255), nullable=False)  # Gmail message ID
    sender = Column(String(255))
    subject = Column(String(255))
    body_snippet = Column(Text)
    received_at = Column(DateTime)
    cached_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)

class CalendarEvent(Base):
    """Cache of calendar events"""
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    event_id = Column(String(255), nullable=False)  # Google Calendar event ID
    title = Column(String(255))
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String(255))
    cached_at = Column(DateTime, default=datetime.utcnow)
