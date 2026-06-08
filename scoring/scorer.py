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
        combined_text = f"{job.job_title} {job.description_text}"
        
        raw_scores, matched_keywords = evaluate_pillars(combined_text)
        
        # Calculate weighted total
        total_score = 0.0
        for pillar, raw in raw_scores.items():
            weight = SCORING_PILLARS[pillar]["weight"]
            total_score += raw * weight
            
        if total_score < MIN_SCORE_THRESHOLD:
            logger.debug(f"Job rejected due to low score: {total_score:.2f} ({job.job_title})")
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
