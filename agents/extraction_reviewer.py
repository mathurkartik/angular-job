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

Your job is to VERIFY the extraction for quality and accuracy.

CRITICAL RULES:
1. You are a VERIFIER, not a creator. Your job is to CHECK the extractor's output against the source text.
2. NEVER add jobs that are not explicitly listed as individual job postings in the source text.
3. NEVER invent job titles, descriptions, or application URLs.
4. If the extractor found zero jobs, return {"reviewed_jobs": [], "changes_made": "No jobs found on page", "hallucinations_found": 0, "jobs_added": 0}.
5. A career page's general "About Us" text, taglines, or search forms are NOT job listings.
6. Every application_url you return MUST be copied exactly from the source text — never construct URLs by appending search query parameters.
7. If a URL looks like a search page (contains ?q=, ?query=, ?keyword=, ?search=) rather than a specific job posting, flag it as suspicious in changes_made but do NOT add it as a new job.

Your ONLY permitted actions are:
- Remove hallucinated/duplicate jobs from the extractor's output
- Fix broken or incorrect URLs in existing jobs
- Correct wrong titles or locations in existing jobs
- Flag quality issues in changes_made

Return a JSON object with:
- "reviewed_jobs": the corrected array of job objects (same schema as input)
- "changes_made": a short string summarizing what you fixed
- "hallucinations_found": integer count of fake jobs you removed
- "jobs_added": 0 (you must NEVER add jobs)
"""


class ExtractionReviewerAgent(BaseGroqAgent):
    def __init__(self):
        super().__init__(name="ExtractionReviewerAgent")

    def review(self, raw_text: str, extracted_jobs: List[Dict[str, Any]], base_url: str) -> Dict[str, Any]:
        """Review extracted jobs against the original text."""
        user_prompt = f"""Base URL: {base_url}

Original Raw Page Text (first 16000 chars):
---
{raw_text[:16000]}
---

Jobs extracted by Agent 1:
```json
{json.dumps(extracted_jobs, indent=2)[:12000]}
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
