"""
Agent 4 — Score Reviewer (Groq)
Reviews Agent 3's scoring output for inflation, deflation, and accuracy.
"""
import json
from typing import Dict, Any, Optional
from agents.base_agent import BaseGroqAgent
from utils.logger import get_logger

logger = get_logger("agent.score_reviewer")

SYSTEM_PROMPT = """You are Agent 4: the Score Reviewer.
You are a calibration expert. You will receive:
1. A job title and description.
2. The scores and justification produced by Agent 3 (the Scorer).

Your job is to REVIEW the scoring for accuracy and calibration.

Check for:
- INFLATED SCORES: Did Agent 3 give a high score (>0.7) to a role that barely mentions Angular?
  If so, lower the score and explain why.
- DEFLATED SCORES: Did Agent 3 give a low score (<0.4) to a role that is clearly Angular-first?
  If so, raise the score and explain why.
- JUSTIFICATION ACCURACY: Does the justification match the actual description content?
- ANGULAR PRIMARY: Is the is_angular_primary flag correct?

You may adjust the total_score by up to ±0.2 if needed.

Return a JSON object with:
- "adjusted_total_score": the final calibrated score (float 0.0-1.0)
- "score_was_adjusted": boolean — did you change the score?
- "adjustment_reason": string explaining any changes (or "Score is accurate")
- "is_angular_primary": your verdict on whether Angular is the primary framework
- "confidence": float 0.0-1.0 indicating how confident you are in this assessment
"""


class ScoreReviewerAgent(BaseGroqAgent):
    def __init__(self):
        super().__init__(name="ScoreReviewerAgent")

    def review(self, job_title: str, description: str, scorer_output: Dict[str, Any]) -> Dict[str, Any]:
        """Review and calibrate Agent 3's scoring."""
        user_prompt = f"""Job Title: {job_title}

Job Description (first 2000 chars):
---
{description[:2000]}
---

Agent 3 (Scorer) produced:
```json
{json.dumps(scorer_output, indent=2)}
```

Review this scoring. Is it accurate, inflated, or deflated?"""

        result = self._call_llm(SYSTEM_PROMPT, user_prompt)

        if not result:
            logger.warning(f"ScoreReviewerAgent returned no result for: {job_title}. Using original score.")
            return {
                "adjusted_total_score": scorer_output.get("total_score", 0.0),
                "score_was_adjusted": False,
                "adjustment_reason": "Review skipped (LLM unavailable)",
                "is_angular_primary": scorer_output.get("is_angular_primary", False),
                "confidence": 0.5,
            }

        adjusted = result.get("score_was_adjusted", False)
        reason = result.get("adjustment_reason", "No adjustment")
        
        if adjusted:
            logger.info(f"ScoreReviewer ADJUSTED '{job_title}': {scorer_output.get('total_score')} → {result.get('adjusted_total_score')} | {reason}")
        else:
            logger.info(f"ScoreReviewer CONFIRMED '{job_title}': {result.get('adjusted_total_score')}")

        return result
