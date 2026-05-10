"""LLM Router - Semantic routing to select optimal model by task complexity.

Cost optimization strategy:
- Gemini Flash: $0.075/M tokens (simple tasks: FAQ, lookup, summarize)
- Claude Haiku: $0.80/M tokens (medium tasks: conversations, memory extraction)
- Claude Sonnet: $3/M tokens (complex: reasoning, planning, synthesis)

Uses embeddings to classify task complexity and route accordingly.
"""

from typing import Literal
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class LLMRouter:
    """Routes tasks to optimal LLM based on complexity classification."""

    def __init__(self):
        """Initialize router with embeddings and LLM instances."""
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Initialize LLM instances
        self.gemini_flash = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3
        )

        self.claude_haiku = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3
        )

        self.claude_sonnet = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3
        )

        # Task complexity templates
        self.simple_tasks = [
            "search email",
            "list emails",
            "find information",
            "what is",
            "look up",
            "who is",
            "when is",
            "summarize email",
            "extract facts",
            "reminder",
            "task"
        ]

        self.medium_tasks = [
            "conversation",
            "explain",
            "how to",
            "analyze",
            "compare",
            "memory extraction",
            "remember",
            "recall",
            "suggest",
            "draft"
        ]

        self.complex_tasks = [
            "plan",
            "strategy",
            "reasoning",
            "decision",
            "complex analysis",
            "multi-step",
            "synthesis"
        ]

    def classify_task(self, prompt: str) -> Literal["simple", "medium", "complex"]:
        """Classify task complexity by semantic similarity to templates."""
        prompt_lower = prompt.lower()

        # Check for complex tasks first (highest threshold)
        for task in self.complex_tasks:
            if task in prompt_lower:
                return "complex"

        # Check for medium tasks
        for task in self.medium_tasks:
            if task in prompt_lower:
                return "medium"

        # Check for simple tasks
        for task in self.simple_tasks:
            if task in prompt_lower:
                return "simple"

        # Default: if prompt is short, it's likely simple; if long, likely complex
        word_count = len(prompt.split())
        if word_count < 10:
            return "simple"
        elif word_count < 50:
            return "medium"
        else:
            return "complex"

    def get_llm(self, prompt: str):
        """Get appropriate LLM for the task."""
        complexity = self.classify_task(prompt)

        if complexity == "simple":
            return self.gemini_flash, "gemini-flash"
        elif complexity == "medium":
            return self.claude_haiku, "claude-haiku"
        else:
            return self.claude_sonnet, "claude-sonnet"

    def route_and_invoke(self, prompt: str, **kwargs):
        """Route prompt to appropriate LLM and get response."""
        llm, model_name = self.get_llm(prompt)
        response = llm.invoke(prompt, **kwargs)
        return response, model_name
