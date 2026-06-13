"""
Agent 1 — Extractor (Groq)
Reads raw page text and extracts structured job listings as JSON.
"""
from typing import List, Dict, Any
from agents.base_agent import BaseGroqAgent
from utils.logger import get_logger

logger = get_logger("agent.extractor")

SYSTEM_PROMPT = """You are Agent 1: the Job Extractor.
You are an expert technical recruiter AI. Your ONLY job is to read raw text
scraped from a company's career/jobs page and extract all Software Engineering,
Frontend, UI, and Full-Stack job listings.

Rules:
- ONLY extract real jobs that are clearly listed in the text.
- DO NOT invent or hallucinate jobs that are not in the text.
- Ignore marketing, sales, HR, design-only, and non-engineering roles.
- If no relevant jobs exist, return an empty array.

Return a JSON object with a single key "jobs" containing an array of objects.
Each object must have:
- "job_title": exact title from the page
- "location": location if mentioned, otherwise "Not specified"
- "application_url": the direct URL to apply (use base_url + relative path if needed)
- "description_text": a short snippet of the role description (max 300 chars)
"""


class ExtractorAgent(BaseGroqAgent):
    def __init__(self):
        super().__init__(name="ExtractorAgent")

    def extract(self, raw_text: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract job listings from raw page text."""
        user_prompt = f"""Base URL: {base_url}

Raw Career Page Text (first 16000 chars):
---
{raw_text[:16000]}
---

Extract all Software Engineering and Frontend job listings from this text."""

        result = self._call_llm(SYSTEM_PROMPT, user_prompt)

        if not result:
            logger.warning("ExtractorAgent returned no result.")
            return []

        jobs = result.get("jobs", [])
        logger.info(f"ExtractorAgent found {len(jobs)} potential jobs from {base_url}")
        return jobs
