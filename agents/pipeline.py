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
    ExportedJobListing, CompanyCategory
)
from agents.extractor_agent import ExtractorAgent
from agents.extraction_reviewer import ExtractionReviewerAgent
from filters.pipeline_router import run_pipeline
from utils.logger import get_logger

logger = get_logger("pipeline")


class AgentPipeline:
    """Orchestrates the 5-agent pipeline for a single company page."""

    def __init__(self):
        self.extractor = ExtractorAgent()
        self.extraction_reviewer = ExtractionReviewerAgent()

    def process_page(
        self,
        raw_text: str,
        company: Dict[str, Any],
        category: CompanyCategory,
    ) -> List[ExportedJobListing]:
        """
        Run the full 2-agent pipeline on a single company's career page text.
        Returns a list of reviewed and validated job listings.
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

        # ── Export ──
        exported_listings: List[ExportedJobListing] = []
        for listing in filtered_listings:
            exported = ExportedJobListing(
                **listing.model_dump()
            )
            exported_listings.append(exported)

        logger.info(f"[Pipeline] {len(exported_listings)} jobs processed for {company_name}")
        return exported_listings

