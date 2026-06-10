"""
Pipeline Orchestrator: Chains all 4 agents together.

Flow:
  Playwright (raw text) -> Agent 1 (Extract) -> Agent 2 (Review Extraction)
  -> Filter Pipeline -> Agent 3 (Score) -> Agent 4 (Review Score)
  -> jobs.json
"""
from typing import List, Dict, Any
from schemas.job_listing import (
    RawJobListing, ReviewedJobListing, FilteredJobListing,
    ScoredJobListing, CompanyCategory
)
from agents.extractor_agent import ExtractorAgent
from agents.extraction_reviewer import ExtractionReviewerAgent
from agents.scorer_agent import ScorerAgent
from agents.score_reviewer import ScoreReviewerAgent
from filters.pipeline_router import run_pipeline
from config.scoring_config import MIN_SCORE_THRESHOLD
from utils.logger import get_logger

logger = get_logger("pipeline")


class AgentPipeline:
    """Orchestrates the 5-agent pipeline for a single company page."""

    def __init__(self):
        self.extractor = ExtractorAgent()
        self.extraction_reviewer = ExtractionReviewerAgent()
        self.scorer = ScorerAgent()
        self.score_reviewer = ScoreReviewerAgent()

    def process_page(
        self,
        raw_text: str,
        company: Dict[str, Any],
        category: CompanyCategory,
    ) -> List[ScoredJobListing]:
        """
        Run the full 5-agent pipeline on a single company's career page text.
        Returns a list of fully scored, reviewed, and validated job listings.
        """
        company_name = company["name"]
        base_url = company["url"]
        tier = company["tier"]

        logger.info(f"=== Pipeline Start: {company_name} ===")

        # ── Agent 1: Extract ──
        logger.info(f"[Agent 1] Extracting jobs from {company_name}...")
        extracted_jobs = self.extractor.extract(raw_text, base_url)

        if not extracted_jobs:
            logger.info(f"[Agent 1] No jobs found for {company_name}. Skipping.")
            return []

        # ── Agent 2: Review Extraction ──
        logger.info(f"[Agent 2] Reviewing {len(extracted_jobs)} extracted jobs...")
        review_result = self.extraction_reviewer.review(raw_text, extracted_jobs, base_url)
        reviewed_jobs_data = review_result.get("reviewed_jobs", extracted_jobs)

        # Convert to ReviewedJobListing models
        reviewed_listings: List[ReviewedJobListing] = []
        for job_data in reviewed_jobs_data:
            try:
                listing = ReviewedJobListing(
                    company_name=company_name,
                    company_tier=tier,
                    category=category,
                    job_title=job_data.get("job_title", "Unknown"),
                    location=job_data.get("location", "Not specified"),
                    description_text=job_data.get("description_text", ""),
                    application_url=job_data.get("application_url", base_url),
                    extraction_verified=True,
                    reviewer_notes=review_result.get("changes_made", ""),
                )
                reviewed_listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to parse reviewed job: {e}")

        # ── Filter Pipeline (existing Python filters) ──
        logger.info(f"[Filters] Running category-specific filter pipeline...")
        filtered_listings: List[FilteredJobListing] = []
        for listing in reviewed_listings:
            # Convert ReviewedJobListing to RawJobListing for the filter pipeline
            raw = RawJobListing(**{
                k: v for k, v in listing.model_dump().items()
                if k in RawJobListing.model_fields
            })
            filtered = run_pipeline(raw)
            if filtered:
                # Upgrade to FilteredJobListing with review fields
                filt = FilteredJobListing(
                    **{k: v for k, v in listing.model_dump().items()
                       if k in FilteredJobListing.model_fields},
                    passed_gates=filtered.passed_gates if hasattr(filtered, 'passed_gates') else [],
                )
                filtered_listings.append(filt)

        logger.info(f"[Filters] {len(filtered_listings)}/{len(reviewed_listings)} passed filters")

        if not filtered_listings:
            return []

        # ── Agent 3 + Agent 4: Score + Review Score ──
        scored_listings: List[ScoredJobListing] = []
        for listing in filtered_listings:
            # Agent 3: Score
            logger.info(f"[Agent 3] Scoring: {listing.job_title}")
            scorer_result = self.scorer.score(listing.job_title, listing.description_text)

            if not scorer_result:
                logger.warning(f"[Agent 3] Scoring failed for {listing.job_title}. Skipping.")
                continue

            total_score = scorer_result.get("total_score", 0.0)

            # Agent 4: Review Score
            logger.info(f"[Agent 4] Reviewing score for: {listing.job_title}")
            review_result = self.score_reviewer.review(
                listing.job_title, listing.description_text, scorer_result
            )

            # Use the adjusted score if the reviewer changed it
            final_score = review_result.get("adjusted_total_score", total_score)

            if final_score < MIN_SCORE_THRESHOLD:
                logger.info(f"[Pipeline] Rejected (score {final_score:.2f} < {MIN_SCORE_THRESHOLD}): {listing.job_title}")
                continue

            # Build the final ScoredJobListing
            scored = ScoredJobListing(
                **listing.model_dump(),
                total_score=final_score,
                pillar_scores=scorer_result.get("pillar_scores", {}),
                matched_keywords=scorer_result.get("matched_keywords", {}),
                justification=f"{scorer_result.get('justification', 'AI evaluated')}",
                score_reviewed=True,
                score_adjusted=review_result.get("score_was_adjusted", False),
                score_reviewer_notes=review_result.get("adjustment_reason", ""),
            )
            scored_listings.append(scored)

        logger.info(f"[Pipeline] {len(scored_listings)} jobs scored and reviewed for {company_name}")
        return scored_listings

