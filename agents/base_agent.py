"""
Base Agent: Provides a unified interface for calling Groq LLMs.
All Groq-based agents (1-4) inherit from this.
"""
import os
import json
from typing import Dict, Any, Optional
from groq import Groq
from utils.logger import get_logger

logger = get_logger("agent.base")


class BaseGroqAgent:
    """Abstract base class for all Groq-powered agents."""

    def __init__(self, name: str, model: str = "llama-3.1-8b-instant"):
        self.name = name
        self.model = model
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning(f"[{self.name}] GROQ_API_KEY not found. Agent will be disabled.")
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Send a structured JSON request to Groq and parse the response."""
        if not self.client:
            logger.warning(f"[{self.name}] Skipped — no Groq client.")
            return None

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for deterministic, factual output
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"[{self.name}] LLM call failed: {str(e)}")
            return None
