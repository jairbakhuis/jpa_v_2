"""Simple agent using LangChain LLM directly."""

import os
from typing import List
from langchain_anthropic import ChatAnthropic
from src.llm_router import LLMRouter
from src.database.connection import get_session
from src.database.models import Memory, Task, Conversation
from sqlalchemy import desc


class JpaAgent:
    """Simple LangChain-based agent for JPA."""

    def __init__(self):
        """Initialize agent."""
        self.router = LLMRouter()
        self.llm = self.router.claude_haiku

    def chat(self, user_message: str, user_id: str) -> str:
        """Process message and return response."""
        llm, model_name = self.router.get_llm(user_message)
        
        # Store conversation
        session = get_session()
        conv = Conversation(
            user_id=user_id,
            user_message=user_message,
            agent_response="",
            model_used=model_name
        )
        session.add(conv)
        session.commit()
        
        try:
            # Simple LLM response
            response = llm.invoke(user_message)
            output = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            output = f"Error: {str(e)}"
        
        # Update conversation
        conv.agent_response = output
        session.commit()
        session.close()
        
        return output

    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """Retrieve conversation history."""
        session = get_session()
        conversations = session.query(Conversation).filter_by(
            user_id=user_id
        ).order_by(desc(Conversation.created_at)).limit(limit).all()
        session.close()

        return [
            {
                "user": conv.user_message,
                "agent": conv.agent_response,
                "model": conv.model_used,
                "timestamp": conv.created_at.isoformat()
            }
            for conv in reversed(conversations)
        ]
