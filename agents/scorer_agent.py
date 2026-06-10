"""
Agent 3 — Scorer (Groq)
Semantically evaluates each job against the 5 scoring pillars.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseGroqAgent
from utils.logger import get_logger

logger = get_logger("agent.scorer")

SYSTEM_PROMPT = """You are Agent 3: the Job Scorer.
You are an expert Angular engineer evaluator. You will receive a job title and description.
Your job is to evaluate how well this role matches a Senior Angular specialist profile.

The candidate profile:
- 8+ years experience, specializing in Angular (v2+), RxJS, TypeScript
- Expert in NgRx/NGXS state management
- Experience with standalone components, Signals, SSR
- Healthcare and Energy domain experience is a bonus
- Looking for roles in Bengaluru, Hyderabad, or fully Remote

Score against these 5 pillars (each 0.0 to 1.0):
1. core_stack: Angular, TypeScript, RxJS, JavaScript, HTML/CSS/SCSS
2. modern_angular: Standalone components, Signals, Angular 17-19, SSR, Hydration, esbuild, Vite
3. state_management: NgRx, NGXS, Akita, Redux, Store patterns
4. testing_quality: Jest, Cypress, Karma, Jasmine, TDD, e2e, code review
5. scale_enterprise: Micro-frontends, Module Federation, Nx, Monorepo, CI/CD, Design Systems, WCAG

Scoring rules:
- 1.0 = This pillar is a PRIMARY requirement in the JD
- 0.5 = Mentioned but not the main focus
- 0.0 = Not mentioned at all
- If the JD says "migrating AWAY from Angular" or Angular is a "nice-to-have", core_stack should be ≤ 0.3

Calculate total_score as weighted average:
  core_stack * 0.30 + modern_angular * 0.25 + state_management * 0.20 + testing_quality * 0.15 + scale_enterprise * 0.10

Return a JSON object with:
- "pillar_scores": object with the 5 pillar scores
- "total_score": the weighted average (float, 0.0-1.0)
- "justification": 1-2 sentence explanation
- "is_angular_primary": boolean — is Angular the MAIN frontend framework for this role?
- "matched_keywords": object mapping each pillar to an array of matched terms found in the text
"""


class ScorerAgent(BaseGroqAgent):
    def __init__(self):
        super().__init__(name="ScorerAgent")

    def score(self, job_title: str, description: str) -> Optional[Dict[str, Any]]:
        """Score a single job listing."""
        user_prompt = f"""Job Title: {job_title}

Job Description:
---
{description[:3000]}
---

Score this job against the 5 pillars for a Senior Angular specialist."""

        result = self._call_llm(SYSTEM_PROMPT, user_prompt)

        if not result:
            logger.warning(f"ScorerAgent returned no result for: {job_title}")
            return None

        logger.info(f"ScorerAgent scored '{job_title}': {result.get('total_score', 'N/A')}")
        return result
