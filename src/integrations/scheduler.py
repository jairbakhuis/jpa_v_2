"""APScheduler setup for reminders and daily briefing"""

import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.config import TIMEZONE, TELEGRAM_USER_ID
from src.database.connection import get_session
from src.database.models import Task, Memory
from src.integrations.telegram_bot import send_notification, send_daily_briefing
from src.memory_utils import MemoryExtractor

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=TIMEZONE)

def check_reminders():
    """Check for due reminders and send notifications"""
    try:
        session = get_session()
        now = datetime.now()

        # Find tasks due now
        pending_tasks = session.query(Task).filter(
            Task.completed == False,
            Task.due_date.isnot(None)
        ).all()

        for task in pending_tasks:
            if task.due_date <= now:
                # Send reminder
                message = f"⏰ Reminder: {task.task}"
                if task.due_date:
                    message += f" (Due: {task.due_date.strftime('%Y-%m-%d %H:%M')})"

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_notification(message))

                task.completed = True
                session.commit()

                logger.info(f"Reminder sent for task: {task.task}")

        session.close()

    except Exception as e:
        logger.error(f"Error checking reminders: {e}")

def generate_daily_briefing():
    """Generate and send daily briefing at 7 AM"""
    try:
        logger.info("Generating daily briefing...")

        briefing = ""

        # Get tasks for today
        session = get_session()
        today = datetime.now().date()
        tasks = session.query(Task).filter(
            Task.completed == False,
            Task.due_date >= datetime.combine(today, datetime.min.time())
        ).all()

        if tasks:
            briefing += "📋 <b>Tasks</b>\n"
            for task in tasks:
                briefing += f"• {task.task}\n"
            briefing += "\n"

        # Get memories
        memories = session.query(Memory).filter_by(
            user_id=str(TELEGRAM_USER_ID)
        ).order_by(Memory.confidence.desc()).limit(3).all()

        if memories:
            briefing += "💭 <b>Key Facts</b>\n"
            for memory in memories:
                briefing += f"• {memory.fact}\n"

        session.close()

        if not briefing:
            briefing = "No tasks or important facts for today."

        # Send briefing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_daily_briefing(briefing))

    except Exception as e:
        logger.error(f"Error generating daily briefing: {e}")

def start_scheduler():
    """Start the scheduler"""
    try:
        # Check reminders every minute
        scheduler.add_job(
            check_reminders,
            trigger=IntervalTrigger(minutes=1),
            id="check_reminders",
            name="Check for due reminders",
            replace_existing=True
        )

        # Daily briefing at 7 AM
        scheduler.add_job(
            generate_daily_briefing,
            trigger=CronTrigger(hour=7, minute=0, timezone=TIMEZONE),
            id="daily_briefing",
            name="Generate daily briefing",
            replace_existing=True
        )

        if not scheduler.running:
            scheduler.start()
            logger.info("✓ Scheduler started")
            logger.info("  - Checking reminders every minute")
            logger.info("  - Daily briefing at 7:00 AM")

    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")

def stop_scheduler():
    """Stop the scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("✓ Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
