"""
Agent 5 — Final Validator (Gemini)
Reviews the entire batch of scored jobs against the original Problem Statement.
Flags jobs that don't meet the requirements. Does NOT auto-reject.
"""
import os
import json
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("agent.final_validator")

# The core requirements from docs/Problem Statement.md, embedded directly
PROBLEM_STATEMENT_SUMMARY = """
CANDIDATE PROFILE REQUIREMENTS:
- 8+ years of experience in frontend engineering
- Specialization: Angular (v2+), RxJS, TypeScript
- Domain preference: Healthcare, Energy (bonus)
- Geographic filter: Bengaluru, Hyderabad, or fully Remote / Global
- Company types: Foreign-HQ product companies, GCCs, premium consultancies (Category 1 = highest priority)

SUCCESS METRICS:
- Precision Rate ≥ 90%: At least 90% of Category 1 output must strictly match the target profile
- Category Isolation 100%: No company from one category should appear in another
- Data Completeness 100%: Every row must have company tier, category, and direct application link

SCORING PILLARS:
1. Core Stack (30%): Angular, TypeScript, RxJS
2. Modern Angular (25%): Standalone Components, Signals, SSR
3. State Management (20%): NgRx, NGXS
4. Testing & Quality (15%): Jest, Cypress, TDD
5. Scale & Enterprise (10%): Micro-frontends, Design Systems, CI/CD
"""


class FinalValidatorAgent:
    """Uses Gemini to review the full batch of jobs against the Problem Statement."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Final Validator (Agent 5) will be disabled.")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini Final Validator initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")

    def validate_batch(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Review a batch of scored jobs against the Problem Statement.
        Returns the jobs with gemini_verdict and gemini_notes added.
        """
        if not self.client:
            logger.warning("Gemini client not available. Marking all jobs as PENDING.")
            for job in jobs:
                job["gemini_verdict"] = "PENDING"
                job["gemini_notes"] = "Gemini review skipped (API key not configured)"
            return jobs

        # Process in batches of 10 to stay within token limits
        batch_size = 10
        validated_jobs = []

        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            reviewed_batch = self._review_batch(batch, batch_num=i // batch_size + 1)
            validated_jobs.extend(reviewed_batch)

        approved = sum(1 for j in validated_jobs if j.get("gemini_verdict") == "APPROVED")
        flagged = sum(1 for j in validated_jobs if j.get("gemini_verdict") == "FLAGGED")
        logger.info(f"Gemini Final Review: {approved} APPROVED, {flagged} FLAGGED out of {len(validated_jobs)} total")

        return validated_jobs

    def _review_batch(self, batch: List[Dict[str, Any]], batch_num: int) -> List[Dict[str, Any]]:
        """Review a single batch of up to 10 jobs."""
        # Build a compact summary of each job for the prompt
        job_summaries = []
        for idx, job in enumerate(batch):
            summary = {
                "index": idx,
                "job_title": job.get("job_title", "Unknown"),
                "company_name": job.get("company_name", "Unknown"),
                "category": job.get("category", "Unknown"),
                "location": job.get("location", "Unknown"),
                "total_score": job.get("total_score", 0.0),
                "justification": job.get("justification", ""),
                "description_snippet": job.get("description_text", "")[:500],
            }
            job_summaries.append(summary)

        prompt = f"""You are Agent 5: the Final Validator.
You are the last quality gate before jobs are shown to the candidate.

Here are the candidate's requirements and success metrics:
{PROBLEM_STATEMENT_SUMMARY}

Below is a batch of {len(batch)} jobs that have been extracted, reviewed, and scored by previous agents.
Your job is to FLAG any job that doesn't meet the requirements above.

IMPORTANT: You do NOT auto-reject. You only FLAG with a reason.
- "APPROVED" = This job clearly matches the candidate profile.
- "FLAGGED" = This job has issues (wrong seniority, wrong framework, wrong location, etc.)

Jobs to review:
```json
{json.dumps(job_summaries, indent=2)}
```

Return a JSON object with a key "verdicts" containing an array of objects.
Each object must have:
- "index": the job index from the input
- "verdict": "APPROVED" or "FLAGGED"
- "notes": A brief explanation (e.g., "Junior role, does not meet 8+ YOE requirement" or "Strong Angular match, approved")
"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                },
            )

            result = json.loads(response.text)
            verdicts = result.get("verdicts", [])

            # Apply verdicts back to the batch
            verdict_map = {v["index"]: v for v in verdicts}
            for idx, job in enumerate(batch):
                if idx in verdict_map:
                    job["gemini_verdict"] = verdict_map[idx].get("verdict", "PENDING")
                    job["gemini_notes"] = verdict_map[idx].get("notes", "")
                else:
                    job["gemini_verdict"] = "PENDING"
                    job["gemini_notes"] = "Not reviewed in this batch"

            logger.info(f"Gemini batch {batch_num}: reviewed {len(verdicts)} jobs")

        except Exception as e:
            logger.error(f"Gemini batch {batch_num} failed: {str(e)}")
            for job in batch:
                job["gemini_verdict"] = "PENDING"
                job["gemini_notes"] = f"Gemini review failed: {str(e)}"

        return batch
