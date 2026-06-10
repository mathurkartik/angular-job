from typing import Optional
from schemas.job_listing import RawJobListing, FilteredJobListing, CompanyCategory
from config.geo_config import CATEGORY1_GEO_WHITELIST, CATEGORY2_GEO_WHITELIST
from filters.geo_filter import GeoFilter
from filters.title_filter import TitleFilter
from utils.jd_fetcher import fetch_jd_text
from utils.logger import get_logger

logger = get_logger("pipeline_router")

async def run_pipeline(job: RawJobListing) -> Optional[FilteredJobListing]:
    """Routes the job to the correct geographic filter based on its category."""
    passed_gates = []
    
    # 1. Global Title Check: Ensure it's a tech role (Fast-Drop layer)
    if not TitleFilter.passes(job.job_title):
        return None
    passed_gates.append("TITLE")
    
    # 2. Geo Filter
    if job.category == CompanyCategory.MAIN:
        if not GeoFilter.passes(job.location, CATEGORY1_GEO_WHITELIST):
            return None
        passed_gates.append("GEO")
    
    elif job.category == CompanyCategory.INDIAN_PRODUCT:
        if not GeoFilter.passes(job.location, CATEGORY2_GEO_WHITELIST):
            return None
        passed_gates.append("GEO")
        
    elif job.category == CompanyCategory.SERVICE:
        passed_gates.append("GEO_BYPASSED")
        
    else:
        # Fallback to strict
        if not GeoFilter.passes(job.location, CATEGORY1_GEO_WHITELIST):
            return None
        passed_gates.append("GEO")

    # 3. Content Check: Fetch JD and check for 'angular'
    logger.info(f"Fetching JD for: {job.job_title} at {job.company_name}")
    jd_text = await fetch_jd_text(job.application_url)
    
    # Also check the title just in case 'angular' is only in the title and not the body
    full_text_to_search = (job.job_title + " " + jd_text).lower()
    
    if "angular" not in full_text_to_search:
        logger.info(f"Dropped {job.job_title} at {job.company_name}: 'angular' not in content.")
        return None
    passed_gates.append("CONTENT_ANGULAR")

    return FilteredJobListing(
        **job.model_dump(),
        passed_gates=passed_gates
    )

