"""
Base Agent: Provides a unified interface for calling Groq LLMs.
All Groq-based agents (1-4) inherit from this.
"""
import os
import json
from typing import Dict, Any, Optional
from groq import Groq
from utils.logger import get_logger
from utils.groq_rate_limiter import GroqRateLimiter

logger = get_logger("agent.base")
rate_limiter = GroqRateLimiter()


class BaseGroqAgent:
    """Abstract base class for all Groq-powered agents."""

    def __init__(self, name: str, model: str = "llama-3.3-70b-versatile"):
        self.name = name
        self.model = model
        
        # Support either a comma-separated list of keys or a single key
        keys_env = os.getenv("GROQ_API_KEYS") or os.getenv("GROQ_API_KEY")
        
        self.api_keys = []
        if keys_env:
            self.api_keys = [k.strip() for k in keys_env.split(",") if k.strip()]
            
        if not self.api_keys:
            logger.warning(f"[{self.name}] GROQ_API_KEY not found. Agent will be disabled.")
            
        self.current_key_idx = 0
        self.client = Groq(api_key=self.api_keys[self.current_key_idx]) if self.api_keys else None

    def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Send a structured JSON request to Groq and parse the response."""
        if not self.client:
            logger.warning(f"[{self.name}] Skipped — no Groq client.")
            return None

        attempts = 0
        max_attempts = len(self.api_keys) if self.api_keys else 1

        while attempts < max_attempts:
            try:
                # Pace calls using the rate limiter (3500 estimated tokens per call)
                rate_limiter.wait_if_needed(3500)
                
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    model=self.model,
                    response_format={"type": "json_object"},
                    temperature=0.1,  # Low temperature for deterministic, factual output
                )
                
                # Update limiter with actual token usage if available
                if response.usage:
                    rate_limiter.update_actual_usage(3500, response.usage.total_tokens)
                
                content = response.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit (429) or invalid key (401)
                if "rate limit" in error_str or "429" in error_str or "401" in error_str or "invalid" in error_str:
                    attempts += 1
                    logger.warning(f"[{self.name}] Groq Error (Rate limit/Invalid key) on key {self.current_key_idx + 1}/{len(self.api_keys)}: {e}")
                    
                    if attempts < max_attempts:
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
                        logger.info(f"[{self.name}] Switching to Groq API Key {self.current_key_idx + 1}...")
                        self.client = Groq(api_key=self.api_keys[self.current_key_idx])
                    else:
                        logger.error(f"[{self.name}] All Groq API keys failed.")
                        return None
                else:
                    logger.error(f"[{self.name}] LLM call failed: {str(e)}")
                    return None
                    
        return None
