import asyncio
import argparse
from typing import List
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file

from schemas.job_listing import CompanyCategory, ExportedJobListing
from config.companies_main import COMPANIES as MAIN_COMPANIES
from config.companies_indian_product import COMPANIES as PRODUCT_COMPANIES
from config.companies_service import COMPANIES as SERVICE_COMPANIES

from scrapers.scraper_factory import get_scraper, is_api_scraper
from agents.pipeline import AgentPipeline
from exporters.csv_exporter import CSVExporter
from exporters.json_exporter import JSONExporter
from exporters.console_reporter import ConsoleReporter
from utils.logger import get_logger

logger = get_logger("main")

# Initialize the 2-agent pipeline once
pipeline = AgentPipeline()


def deduplicate_jobs(jobs: list) -> list:
    """Remove duplicate jobs based on (company_name, job_title, location)."""
    seen = set()
    unique = []
    for job in jobs:
        key = (
            job.company_name.lower().strip(),
            job.job_title.lower().strip(),
            job.location.lower().strip(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(job)
        else:
            logger.info(f"Deduplicated: {job.job_title} at {job.company_name}")
    return unique


async def process_category(companies: List[dict], category: CompanyCategory, headless: bool) -> List[ExportedJobListing]:
    """Scrape each company's page, then run it through the 2-agent pipeline."""
    exported_jobs = []

    for company in companies:
        try:
            scraper = get_scraper(company["portal_type"], headless=headless)
            portal = company["portal_type"]

            if is_api_scraper(portal):
                # Specialized scrapers have their own scrape() method — use them directly
                logger.info(f"Using specialized {portal} scraper for {company['name']}")
                raw_jobs = await scraper.scrape(company, category)
            else:
                raw_jobs = None

            if raw_jobs is None:
                # Fallback to GenericScraper browser + 2-agent pipeline
                logger.info(f"Using 2-agent pipeline for {company['name']}")
                
                if is_api_scraper(portal):
                    from scrapers.generic_scraper import GenericScraper
                    active_scraper = GenericScraper(headless=headless)
                else:
                    active_scraper = scraper

                raw_text = await active_scraper.get_page_text(company)

                if not raw_text:
                    logger.warning(f"No text extracted from {company['name']}. Skipping.")
                    continue

                jobs = await pipeline.process_page(raw_text, company, category)
                exported_jobs.extend(jobs)
            else:
                # Run each raw job through the filter
                for raw_job in raw_jobs:
                    from filters.pipeline_router import run_pipeline
                    filtered = await run_pipeline(raw_job)
                    if filtered:
                        exported = ExportedJobListing(
                            **filtered.model_dump()
                        )
                        exported_jobs.append(exported)

        except Exception as e:
            logger.error(f"Error processing {company['name']}: {str(e)}")

    return exported_jobs


async def main():
    parser = argparse.ArgumentParser(description="Automated Senior Angular Job Scraper — 5-Agent AI Pipeline")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode (visible)")
    parser.add_argument("--category", type=str, choices=["all", "main", "product", "service"], default="all", help="Which category to scrape")
    args = parser.parse_args()

    headless = not args.headed
    all_exported_jobs = []

    logger.info("==========================================================")
    logger.info("|  Angular Job Engine - 2-Agent Pipeline                 |")
    logger.info("|  Agents: Extractor -> Reviewer (Scoring Disabled)      |")
    logger.info("==========================================================")

    if args.category in ["all", "main"]:
        logger.info("\n=== Processing Category 1: Main Companies ===")
        jobs = await process_category(MAIN_COMPANIES, CompanyCategory.MAIN, headless)
        all_exported_jobs.extend(jobs)

    if args.category in ["all", "product"]:
        logger.info("\n=== Processing Category 2: Indian Product Companies ===")
        jobs = await process_category(PRODUCT_COMPANIES, CompanyCategory.INDIAN_PRODUCT, headless)
        all_exported_jobs.extend(jobs)

    if args.category in ["all", "service"]:
        logger.info("\n=== Processing Category 3: Service Companies ===")
        jobs = await process_category(SERVICE_COMPANIES, CompanyCategory.SERVICE, headless)
        all_exported_jobs.extend(jobs)


    # ── Deduplicate, Rank and Export ──
    logger.info("\nDeduplicating, Ranking and Exporting Results...")
    all_exported_jobs = deduplicate_jobs(all_exported_jobs)
    # Sort by category priority
    cat_order = {"main": 1, "indian_product": 2, "service": 3}
    all_exported_jobs.sort(key=lambda j: cat_order.get(j.category.value, 99))
    for i, job in enumerate(all_exported_jobs):
        job.rank = i + 1

    CSVExporter.export(all_exported_jobs)
    JSONExporter.export(all_exported_jobs)
    ConsoleReporter.report(all_exported_jobs)

    logger.info(f"\n{'='*50}")
    logger.info(f"FINAL RESULTS: {len(all_exported_jobs)} total jobs found")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())
