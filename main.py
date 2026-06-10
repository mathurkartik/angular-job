import asyncio
import argparse
from typing import List

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
            # Step 1: Use Playwright to load the page and extract raw text
            scraper = get_scraper(company["portal_type"], headless=headless)
            raw_text = await scraper.get_page_text(company)

            if not raw_text:
                logger.warning(f"No text extracted from {company['name']}. Skipping.")
                continue

            # Step 2: Run the 5-agent pipeline (Extract → Review → Filter → Score → Review Score)
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

    logger.info("╔════════════════════════════════════════════════════════╗")
    logger.info("║  Angular Job Engine — 5-Agent AI Pipeline             ║")
    logger.info("║  Agents: Extractor → Reviewer → Scorer → Reviewer    ║")
    logger.info("║  Final Gate: Gemini Validator                         ║")
    logger.info("╚════════════════════════════════════════════════════════╝")

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

    # ── Agent 5: Gemini Final Validation (runs once on the entire batch) ──
    logger.info("\n=== Running Gemini Final Validation ===")
    all_scored_jobs = pipeline.final_review(all_scored_jobs)

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

    # Summary
    approved = sum(1 for j in all_scored_jobs if j.gemini_verdict == "APPROVED")
    flagged = sum(1 for j in all_scored_jobs if j.gemini_verdict == "FLAGGED")
    logger.info(f"\n{'='*50}")
    logger.info(f"FINAL RESULTS: {len(all_scored_jobs)} total jobs")
    logger.info(f"  ✅ Gemini APPROVED: {approved}")
    logger.info(f"  ⚠️  Gemini FLAGGED:  {flagged}")
    logger.info(f"  ⏳ Pending Review:   {len(all_scored_jobs) - approved - flagged}")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())
