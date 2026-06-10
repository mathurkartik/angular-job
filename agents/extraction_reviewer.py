"""
Agent 2 — Extraction Reviewer (Groq)
Reviews Agent 1's output against the original page text.
Catches hallucinations, missing jobs, broken URLs, and duplicates.
"""
import json
from typing import List, Dict, Any
from agents.base_agent import BaseGroqAgent
from utils.logger import get_logger

logger = get_logger("agent.extraction_reviewer")

SYSTEM_PROMPT = """You are Agent 2: the Extraction Reviewer.
You are a meticulous QA agent. You will receive:
1. The original raw text from a career page.
2. A list of jobs that Agent 1 (the Extractor) extracted.

Your job is to REVIEW the extraction for quality and accuracy.

Check for these issues:
- HALLUCINATED JOBS: Did Agent 1 invent a job that does NOT exist in the original text? Remove it.
- MISSING JOBS: Did Agent 1 miss an obvious Software Engineering / Frontend / Angular job? Add it.
- BROKEN URLs: Are the application_url values plausible? Fix obviously wrong URLs.
- DUPLICATES: Are any listings repeated? Remove duplicates.
- WRONG TITLES: Did Agent 1 misread or truncate a job title? Correct it.

Return a JSON object with:
- "reviewed_jobs": the corrected array of job objects (same schema as input)
- "changes_made": a short string summarizing what you fixed (e.g., "Removed 1 hallucinated job, added 1 missed Angular listing")
- "hallucinations_found": integer count of fake jobs you removed
- "jobs_added": integer count of missing jobs you added
"""


class ExtractionReviewerAgent(BaseGroqAgent):
    def __init__(self):
        super().__init__(name="ExtractionReviewerAgent")

    def review(self, raw_text: str, extracted_jobs: List[Dict[str, Any]], base_url: str) -> Dict[str, Any]:
        """Review extracted jobs against the original text."""
        user_prompt = f"""Base URL: {base_url}

Original Raw Page Text (first 4000 chars):
---
{raw_text[:4000]}
---

Jobs extracted by Agent 1:
```json
{json.dumps(extracted_jobs, indent=2)[:3000]}
```

Review these extracted jobs against the original text. Fix any issues."""

        result = self._call_llm(SYSTEM_PROMPT, user_prompt)

        if not result:
            logger.warning("ExtractionReviewerAgent returned no result. Passing through original jobs.")
            return {
                "reviewed_jobs": extracted_jobs,
                "changes_made": "Review skipped (LLM unavailable)",
                "hallucinations_found": 0,
                "jobs_added": 0,
            }

        changes = result.get("changes_made", "No changes")
        hallucinations = result.get("hallucinations_found", 0)
        added = result.get("jobs_added", 0)

        logger.info(f"ExtractionReviewer: {changes} | Hallucinations: {hallucinations} | Added: {added}")

        return {
            "reviewed_jobs": result.get("reviewed_jobs", extracted_jobs),
            "changes_made": changes,
            "hallucinations_found": hallucinations,
            "jobs_added": added,
        }
