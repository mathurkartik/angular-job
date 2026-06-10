import asyncio
import argparse
from typing import List
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file

from schemas.job_listing import CompanyCategory, ScoredJobListing
from config.companies_main import COMPANIES as MAIN_COMPANIES
from config.companies_indian_product import COMPANIES as PRODUCT_COMPANIES
from config.companies_service import COMPANIES as SERVICE_COMPANIES

from scrapers.scraper_factory import get_scraper
from agents.pipeline import AgentPipeline
from exporters.csv_exporter import CSVExporter
from exporters.json_exporter import JSONExporter
from exporters.console_reporter import ConsoleReporter
from utils.logger import get_logger

logger = get_logger("main")

# Initialize the 5-agent pipeline once
pipeline = AgentPipeline()


async def process_category(companies: List[dict], category: CompanyCategory, headless: bool) -> List[ScoredJobListing]:
    """Scrape each company's page, then run it through the 5-agent pipeline."""
    scored_jobs = []

    for company in companies:
        try:
            scraper = get_scraper(company["portal_type"], headless=headless)
            portal = company["portal_type"]

            if portal in ("greenhouse", "lever", "workday"):
                # Specialized scrapers have their own extract_jobs() — use them directly
                logger.info(f"Using specialized {portal} scraper for {company['name']}")
                raw_jobs = await scraper.scrape(company, category)

                # Run each raw job through the filter + AI scoring agents (Agents 3-5)
                for raw_job in raw_jobs:
                    from filters.pipeline_router import run_pipeline
                    filtered = run_pipeline(raw_job)
                    if filtered:
                        scored = ScoredJobListing(
                            **filtered.model_dump(),
                            total_score=1.0,
                            pillar_scores={"core_stack": 1.0, "modern_angular": 1.0, "state_management": 1.0, "testing_quality": 1.0, "scale_enterprise": 1.0},
                            matched_keywords={},
                            justification="AI Scoring Disabled. Raw extracted job.",
                            score_reviewed=False,
                            score_adjusted=False,
                            score_reviewer_notes=""
                        )
                        scored_jobs.append(scored)
            else:
                # Generic portals — use the full 5-agent AI pipeline
                logger.info(f"Using 5-agent AI pipeline for {company['name']}")
                raw_text = await scraper.get_page_text(company)

                if not raw_text:
                    logger.warning(f"No text extracted from {company['name']}. Skipping.")
                    continue

                jobs = pipeline.process_page(raw_text, company, category)
                scored_jobs.extend(jobs)

        except Exception as e:
            logger.error(f"Error processing {company['name']}: {str(e)}")

    return scored_jobs


async def main():
    parser = argparse.ArgumentParser(description="Automated Senior Angular Job Scraper — 5-Agent AI Pipeline")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode (visible)")
    parser.add_argument("--category", type=str, choices=["all", "main", "product", "service"], default="all", help="Which category to scrape")
    args = parser.parse_args()

    headless = not args.headed
    all_scored_jobs = []

    logger.info("==========================================================")
    logger.info("|  Angular Job Engine - 2-Agent Pipeline                 |")
    logger.info("|  Agents: Extractor -> Reviewer (Scoring Disabled)      |")
    logger.info("==========================================================")

    if args.category in ["all", "main"]:
        logger.info("\n=== Processing Category 1: Main Companies ===")
        jobs = await process_category(MAIN_COMPANIES, CompanyCategory.MAIN, headless)
        all_scored_jobs.extend(jobs)

    if args.category in ["all", "product"]:
        logger.info("\n=== Processing Category 2: Indian Product Companies ===")
        jobs = await process_category(PRODUCT_COMPANIES, CompanyCategory.INDIAN_PRODUCT, headless)
        all_scored_jobs.extend(jobs)

    if args.category in ["all", "service"]:
        logger.info("\n=== Processing Category 3: Service Companies ===")
        jobs = await process_category(SERVICE_COMPANIES, CompanyCategory.SERVICE, headless)
        all_scored_jobs.extend(jobs)


    # ── Rank and Export ──
    logger.info("\nRanking and Exporting Results...")
    # Sort by category priority then score descending
    cat_order = {"main": 1, "indian_product": 2, "service": 3}
    all_scored_jobs.sort(key=lambda j: (cat_order.get(j.category.value, 99), -j.total_score))
    for i, job in enumerate(all_scored_jobs):
        job.rank = i + 1

    CSVExporter.export(all_scored_jobs)
    JSONExporter.export(all_scored_jobs)
    ConsoleReporter.report(all_scored_jobs)

    logger.info(f"\n{'='*50}")
    logger.info(f"FINAL RESULTS: {len(all_scored_jobs)} total jobs found")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())
