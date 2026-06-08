from typing import Optional, List
from schemas.job_listing import FilteredJobListing, ScoredJobListing
from scoring.pillars import evaluate_pillars
from scoring.justification import generate_justification
from config.scoring_config import SCORING_PILLARS, MIN_SCORE_THRESHOLD
from utils.logger import get_logger

logger = get_logger("scoring")

class Scorer:
    """Scores a filtered job listing and returns a ScoredJobListing if it meets the threshold."""

    @staticmethod
    def score_job(job: FilteredJobListing) -> Optional[ScoredJobListing]:
        from utils.groq_client import groq_client
        
        groq_result = groq_client.score_job_description(job.job_title, job.description_text)
        
        if groq_result:
            # We used Groq successfully!
            total_score = groq_result.get("total_score", 0.0)
            justification = groq_result.get("justification", "Groq evaluation.")
            
            if total_score < MIN_SCORE_THRESHOLD:
                logger.debug(f"Job rejected by Groq: {total_score:.2f} ({job.job_title})")
                return None
                
            return ScoredJobListing(
                **job.model_dump(),
                total_score=total_score,
                pillar_scores={"groq_semantic_eval": total_score},
                matched_keywords={"groq_flags": ["is_angular_primary"] if groq_result.get("is_angular_primary") else []},
                justification=f"🤖 {justification}"
            )
        else:
            # Fallback to keyword scoring
            combined_text = f"{job.job_title} {job.description_text}"
            raw_scores, matched_keywords = evaluate_pillars(combined_text)
            
            total_score = sum(raw * SCORING_PILLARS[pillar]["weight"] for pillar, raw in raw_scores.items())
            
            if total_score < MIN_SCORE_THRESHOLD:
                return None
                
            justification = generate_justification(matched_keywords, total_score)
            return ScoredJobListing(
                **job.model_dump(),
                total_score=total_score,
                pillar_scores=raw_scores,
                matched_keywords=matched_keywords,
                justification=justification
            )

    @staticmethod
    def rank_jobs(jobs: List[ScoredJobListing]) -> List[ScoredJobListing]:
        """Sorts jobs by category priority, then by score descending."""
        # Custom sort order for categories (Main > Product > Service)
        cat_order = {
            "main": 1,
            "indian_product": 2,
            "service": 3
        }
        
        sorted_jobs = sorted(
            jobs,
            key=lambda j: (cat_order.get(j.category.value, 99), -j.total_score)
        )
        
        # Assign ranks
        for i, job in enumerate(sorted_jobs):
            job.rank = i + 1
            
        return sorted_jobs
