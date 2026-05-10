"""Memory utilities using memory-template pattern.

Integrates fact extraction and storage with debouncing.
Based on: https://github.com/jairbakhuis/memory-template

Modes:
- insert: New facts/events
- patch: Update existing facts (profiles)
"""

import json
import os
from typing import Dict, List, Any
from langchain_anthropic import ChatAnthropic
from src.database.connection import get_db
from src.database.models import Memory
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """Extract facts from conversations using Claude."""

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.2
        )

        # Debounce window: don't extract same fact within 6 hours
        self.debounce_hours = 6

    def extract_facts(self, conversation: str, mode: str = "insert") -> List[Dict[str, Any]]:
        """Extract facts from conversation using Claude.

        Args:
            conversation: The conversation text
            mode: "insert" for new facts, "patch" for updates

        Returns:
            List of extracted facts with categories and confidence
        """
        if mode == "insert":
            prompt = f"""Extract NEW FACTS, EVENTS, or NOTES from this conversation.
Only extract information the user explicitly mentioned.
Return as JSON array with fields: fact, category, confidence.
Categories: family, work, interests, general.

Conversation:
{conversation}

JSON:"""
        else:  # patch mode
            prompt = f"""Extract PROFILE UPDATES from this conversation.
Look for changes to existing facts about the user.
Return as JSON array with fields: fact, category, confidence.

Conversation:
{conversation}

JSON:"""

        response = self.llm.invoke(prompt)
        content = response.content

        # Parse JSON from response
        try:
            # Find JSON array in response
            start = content.find('[')
            end = content.rfind(']') + 1
            json_str = content[start:end]
            facts = json.loads(json_str)
            return facts
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse facts: {e}")
            return []

    def store_facts(self, facts: List[Dict[str, Any]], user_id: str, mode: str = "insert"):
        """Store facts with debouncing to avoid duplicates."""
        session = get_db()

        for fact in facts:
            fact_text = fact.get("fact", "")
            category = fact.get("category", "general")
            confidence = fact.get("confidence", 0.8)

            if not fact_text:
                continue

            # Check if similar fact exists (debouncing)
            if mode == "insert":
                # For new facts, check if exact fact exists recently
                recent_cutoff = datetime.utcnow() - timedelta(hours=self.debounce_hours)
                existing = session.query(Memory).filter(
                    Memory.fact.like(f"%{fact_text[:50]}%"),
                    Memory.category == category,
                    Memory.created_at >= recent_cutoff
                ).first()

                if existing:
                    # Update confidence instead of creating duplicate
                    existing.confidence = min(1.0, existing.confidence + 0.1)
                    logger.info(f"Updated existing memory: {fact_text[:50]}")
                    continue

            # Store new fact
            memory = Memory(
                fact=fact_text,
                category=category,
                confidence=confidence,
                user_id=user_id,
                mode=mode
            )
            session.add(memory)
            logger.info(f"Stored fact: {fact_text[:50]}")

        session.commit()
        session.close()

    def get_memories(self, user_id: str, category: str = None, limit: int = 10) -> List[str]:
        """Retrieve memories for user."""
        session = get_db()

        query = session.query(Memory).filter_by(user_id=user_id)
        if category:
            query = query.filter_by(category=category)

        memories = query.order_by(Memory.confidence.desc()).limit(limit).all()
        session.close()

        return [m.fact for m in memories]


def extract_and_store(conversation: str, user_id: str, mode: str = "insert"):
    """Convenience function to extract and store facts in one call."""
    extractor = MemoryExtractor()
    facts = extractor.extract_facts(conversation, mode)
    extractor.store_facts(facts, user_id, mode)
    return len(facts)
