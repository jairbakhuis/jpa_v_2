"""JPA - Jair's Personal Assistant

Architecture (LangChain + LangGraph):
- LLM Router: Semantic routing to select optimal model (Gemini Flash → Haiku → Sonnet)
- Agent: LangChain initialize_agent with GmailToolkit + custom tools
- Memory: Memory-template pattern with debouncing for fact extraction
- Database: PostgreSQL with SQLAlchemy ORM
- Telegram: FastAPI webhook integration
- Scheduler: APScheduler for reminders and daily briefing
"""

__version__ = "1.0.0"
__author__ = "Jair Bakhuis"
