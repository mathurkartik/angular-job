import asyncio
from asgiref.sync import async_to_sync
from workers.celery_app import celery_app
from schemas.job_listing import CompanyCategory
from config.companies_main import COMPANIES as MAIN_COMPANIES
from config.companies_indian_product import COMPANIES as PRODUCT_COMPANIES
from config.companies_service import COMPANIES as SERVICE_COMPANIES
from db.database import AsyncSessionLocal
from crud.jobs import upsert_job
from scrapers.scraper_factory import get_scraper
from filters.pipeline_router import run_pipeline
from scoring.scorer import Scorer
from utils.logger import get_logger

logger = get_logger("celery.tasks")

async def _run_scrape_async(category_name: str, headless: bool):
    """Core async logic for scraping a category."""
    if category_name == "main":
        companies = MAIN_COMPANIES
        category = CompanyCategory.MAIN
    elif category_name == "indian_product":
        companies = PRODUCT_COMPANIES
        category = CompanyCategory.INDIAN_PRODUCT
    elif category_name == "service":
        companies = SERVICE_COMPANIES
        category = CompanyCategory.SERVICE
    else:
        logger.error(f"Unknown category: {category_name}")
        return 0

    jobs_upserted = 0
    
    async with AsyncSessionLocal() as db:
        for company in companies:
            try:
                scraper = get_scraper(company["portal_type"], headless=headless)
                raw_jobs = await scraper.scrape(company, category)
                
                for raw_job in raw_jobs:
                    filtered_job = run_pipeline(raw_job)
                    if filtered_job:
                        scored_job = Scorer.score_job(filtered_job)
                        if scored_job:
                            await upsert_job(db, scored_job)
                            jobs_upserted += 1
            except Exception as e:
                logger.error(f"Error scraping {company['name']}: {str(e)}")
                
    return jobs_upserted

@celery_app.task(name="scrape_category", bind=True)
def scrape_category_task(self, category_name: str, headless: bool = True):
    """
    Celery task to run the scraper for a specific category.
    Uses asgiref to bridge Celery's sync worker with our async scraper engine.
    """
    logger.info(f"Starting Celery scrape task for category: {category_name}")
    
    result = async_to_sync(_run_scrape_async)(category_name, headless)
    
    logger.info(f"Completed scrape task for {category_name}. Found {result} valid jobs.")
    return {"status": "SUCCESS", "jobs_found": result}
