"""Agent using LangChain's initialize_agent pattern with official toolkits.

Uses:
- LangChain's GmailToolkit for email operations
- LangChain's AgentExecutor for tool orchestration
- Custom tools for memory and reminders (not available in LangChain)
"""

import os
from typing import List, Any
from langchain.agents import initialize_agent, Tool
from langchain_gmail import GmailToolkit
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from src.llm_router import LLMRouter
from src.database.connection import get_session
from src.database.models import Memory, Task, Conversation
from sqlalchemy import desc


def create_memory_tool():
    """Tool to store facts in memory."""
    def remember_fact(fact: str, category: str = "general"):
        session = get_session()
        memory = Memory(
            fact=fact,
            category=category,
            confidence=0.9
        )
        session.add(memory)
        session.commit()
        session.close()
        return f"Stored fact: {fact}"

    return Tool(
        name="remember_fact",
        func=remember_fact,
        description="Store a fact or piece of information in memory with a category (family, work, interests, general)"
    )


def create_recall_tool():
    """Tool to retrieve memories."""
    def recall_facts(category: str = None):
        session = get_session()
        if category:
            memories = session.query(Memory).filter_by(category=category).order_by(desc(Memory.created_at)).limit(10).all()
        else:
            memories = session.query(Memory).order_by(desc(Memory.created_at)).limit(10).all()
        session.close()

        if not memories:
            return "No memories found"

        return "\n".join([f"- {m.fact} ({m.category})" for m in memories])

    return Tool(
        name="recall_facts",
        func=recall_facts,
        description="Recall stored facts from memory, optionally filtered by category"
    )


def create_reminder_tool():
    """Tool to create reminders."""
    def create_reminder(task: str, due_date: str):
        session = get_session()
        reminder = Task(
            task=task,
            due_date=due_date,
            completed=False
        )
        session.add(reminder)
        session.commit()
        session.close()
        return f"Reminder created: {task} due on {due_date}"

    return Tool(
        name="create_reminder",
        func=create_reminder,
        description="Create a reminder or task with a due date (format: YYYY-MM-DD HH:MM)"
    )


class JpaAgent:
    """LangChain-based agent for JPA."""

    def __init__(self):
        """Initialize agent with LangChain's initialize_agent."""
        self.router = LLMRouter()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize Gmail toolkit
        gmail_toolkit = GmailToolkit()
        gmail_tools = gmail_toolkit.get_tools()

        # Custom tools
        custom_tools = [
            create_memory_tool(),
            create_recall_tool(),
            create_reminder_tool()
        ]

        all_tools = gmail_tools + custom_tools

        # Get initial LLM (will be updated per message based on routing)
        self.base_llm = self.router.claude_haiku

        # Initialize agent with LangChain's official pattern
        self.agent_executor = initialize_agent(
            tools=all_tools,
            llm=self.base_llm,
            agent="zero-shot-react-description",
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )

    def chat(self, user_message: str, user_id: str) -> str:
        """Process user message and return response."""
        # Route to appropriate LLM based on task complexity
        llm, model_name = self.router.get_llm(user_message)

        # Update agent's LLM if it's complex
        if model_name != "claude-haiku":
            self.agent_executor.agent.llm_chain.llm = llm

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

        # Invoke agent
        response = self.agent_executor.invoke({"input": user_message})
        output = response.get("output", "I couldn't process that.")

        # Update conversation with response
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
