import asyncio
import argparse
from typing import List

from schemas.job_listing import CompanyCategory, ScoredJobListing
from config.companies_main import COMPANIES as MAIN_COMPANIES
from config.companies_indian_product import COMPANIES as PRODUCT_COMPANIES
from config.companies_service import COMPANIES as SERVICE_COMPANIES

from scrapers.scraper_factory import get_scraper
from filters.pipeline_router import run_pipeline
from scoring.scorer import Scorer
from exporters.csv_exporter import CSVExporter
from exporters.json_exporter import JSONExporter
from exporters.console_reporter import ConsoleReporter
from utils.logger import get_logger

logger = get_logger("main")

async def process_category(companies: List[dict], category: CompanyCategory, headless: bool) -> List[ScoredJobListing]:
    scored_jobs = []
    
    for company in companies:
        scraper = get_scraper(company["portal_type"], headless=headless)
        raw_jobs = await scraper.scrape(company, category)
        
        for raw_job in raw_jobs:
            filtered_job = run_pipeline(raw_job)
            if filtered_job:
                scored_job = Scorer.score_job(filtered_job)
                if scored_job:
                    scored_jobs.append(scored_job)
                    
    return scored_jobs

async def main():
    parser = argparse.ArgumentParser(description="Automated Senior Angular Job Scraper")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode (visible)")
    parser.add_argument("--category", type=str, choices=["all", "main", "product", "service"], default="all", help="Which category to scrape")
    args = parser.parse_args()
    
    headless = not args.headed
    all_scored_jobs = []
    
    logger.info("Starting Automated Job Acquisition Engine...")
    
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
        
    logger.info("\nRanking and Exporting Results...")
    ranked_jobs = Scorer.rank_jobs(all_scored_jobs)
    
    CSVExporter.export(ranked_jobs)
    JSONExporter.export(ranked_jobs)
    ConsoleReporter.report(ranked_jobs)

if __name__ == "__main__":
    # Ensure Playwright async runs correctly on Windows
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(main())
