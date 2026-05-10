"""Telegram bot integration using FastAPI webhook"""

import logging
from fastapi import APIRouter, Request
from telegram import Update, Bot
from telegram.error import TelegramError

from src.config import TELEGRAM_TOKEN, TELEGRAM_USER_ID
from src.agent import JpaAgent

logger = logging.getLogger(__name__)

router = APIRouter()
bot = Bot(token=TELEGRAM_TOKEN)

# Initialize agent (singleton)
_agent = None

def get_agent():
    """Get or initialize agent"""
    global _agent
    if _agent is None:
        _agent = JpaAgent()
    return _agent

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook"""
    try:
        data = await request.json()
        update = Update.de_json(data, bot)

        if not update:
            return {"ok": True}

        # Only process messages from authorized user
        if update.message and update.message.from_user.id != TELEGRAM_USER_ID:
            logger.warning(f"Unauthorized user: {update.message.from_user.id}")
            return {"ok": False}

        # Handle message
        if update.message and update.message.text:
            user_message = update.message.text

            # Typing indicator
            await bot.send_chat_action(
                chat_id=TELEGRAM_USER_ID,
                action="typing"
            )

            # Get agent response
            agent = get_agent()
            response = agent.chat(user_message, str(TELEGRAM_USER_ID))

            # Send response
            await bot.send_message(
                chat_id=TELEGRAM_USER_ID,
                text=response,
                parse_mode="HTML"
            )

            logger.info(f"Message processed: {user_message[:50]}...")

        return {"ok": True}

    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
        return {"ok": False}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return {"ok": False}

async def send_notification(message: str):
    """Send notification to user"""
    try:
        await bot.send_message(
            chat_id=TELEGRAM_USER_ID,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Notification sent: {message[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return False

async def send_daily_briefing(briefing_text: str):
    """Send daily briefing"""
    try:
        await bot.send_message(
            chat_id=TELEGRAM_USER_ID,
            text=f"<b>📋 Daily Briefing</b>\n\n{briefing_text}",
            parse_mode="HTML"
        )
        logger.info("Daily briefing sent")
        return True
    except Exception as e:
        logger.error(f"Error sending briefing: {e}")
        return False
