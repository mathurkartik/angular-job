import csv
from pathlib import Path
from typing import Optional
from schemas.job_listing import RawJobListing, FilteredJobListing, CompanyCategory
from config.geo_config import CATEGORY1_GEO_WHITELIST, CATEGORY2_GEO_WHITELIST
from filters.geo_filter import GeoFilter
from filters.title_filter import TitleFilter
from utils.jd_fetcher import fetch_jd_text
from utils.logger import get_logger

logger = get_logger("pipeline_router")

_DROP_LOG_PATH = "output/dropped.csv"
_drop_log_initialized = False

# Gate 4: Title-level negative stack filter
# If the title explicitly names a non-Angular primary stack, drop it.
# This catches .Net/Java/Python roles that passed content check because
# the company page or other listings mention Angular.
NON_ANGULAR_TITLE_INDICATORS = [
    # Explicit stack names in titles
    ".net", "dotnet", "c#", "csharp",
    "java developer", "java engineer", "fullstack java", "full stack java", "full-stack java",
    "python developer", "python engineer",
    "ruby developer", "ruby engineer",
    "golang", "go developer",
    # Completely unrelated roles
    "openwrt", "rdk",
    "linux platform",
    "design engineer",
    "lead engineer",       # too generic, usually mechanical/electrical when no stack specified
    "network engineer",
    "embedded",
    "firmware",
    "hardware",
    # Backend-only indicators (when no frontend/angular/ui qualifier present)
    "backend developer", "back-end developer", "back end developer",
]

# Some titles contain a negative indicator BUT also explicitly say Angular — keep those
# e.g., "Full Stack Java + Angular Developer" should NOT be dropped
ANGULAR_TITLE_OVERRIDES = ["angular", "frontend", "front-end", "front end", "ui engineer", "ui developer"]


def _log_drop(company: str, title: str, gate: str, reason: str):
    """Append a dropped-job record to output/dropped.csv"""
    global _drop_log_initialized
    Path(_DROP_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

    if not _drop_log_initialized:
        with open(_DROP_LOG_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Company", "Job Title", "Failed Gate", "Reason"])
        _drop_log_initialized = True

    with open(_DROP_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([company, title, gate, reason])

async def run_pipeline(job: RawJobListing) -> Optional[FilteredJobListing]:
    """Routes the job to the correct geographic filter based on its category."""
    passed_gates = []
    
    # 1. Global Title Check: Ensure it's a tech role (Fast-Drop layer)
    if not TitleFilter.passes(job.job_title):
        _log_drop(job.company_name, job.job_title, "TITLE", "No tech keyword or excluded keyword matched")
        return None
    passed_gates.append("TITLE")
    
    # 2. Geo Filter
    if job.category == CompanyCategory.MAIN:
        if not GeoFilter.passes(job.location, CATEGORY1_GEO_WHITELIST):
            _log_drop(job.company_name, job.job_title, "GEO", f"Location '{job.location}' not in whitelist")
            return None
        passed_gates.append("GEO")
    
    elif job.category == CompanyCategory.INDIAN_PRODUCT:
        if not GeoFilter.passes(job.location, CATEGORY2_GEO_WHITELIST):
            _log_drop(job.company_name, job.job_title, "GEO", f"Location '{job.location}' not in whitelist")
            return None
        passed_gates.append("GEO")
        
    elif job.category == CompanyCategory.SERVICE:
        # Even for service companies, reject locations that are clearly outside India
        loc = job.location.lower().strip()
        if any(marker in loc for marker in GeoFilter.NON_INDIA_MARKERS):
            _log_drop(job.company_name, job.job_title, "GEO",
                      f"Service company but location '{job.location}' is outside India")
            return None
        passed_gates.append("GEO_BYPASSED")
        
    else:
        # Fallback to strict
        if not GeoFilter.passes(job.location, CATEGORY1_GEO_WHITELIST):
            _log_drop(job.company_name, job.job_title, "GEO", f"Location '{job.location}' not in whitelist")
            return None
        passed_gates.append("GEO")

    # 3. Content Check: Fetch JD and check for 'angular'
    jd_text = ""
    if job.source == "ats_api" and job.description_text and len(job.description_text.strip()) > 100:
        logger.info(f"Using API-provided JD text ({len(job.description_text)} chars) for {job.job_title} at {job.company_name}")
        jd_text = job.description_text
    else:
        logger.info(f"Fetching JD for: {job.job_title} at {job.company_name}")
        jd_text = await fetch_jd_text(job.application_url)
    
    # Also check the title just in case 'angular' is only in the title and not the body
    full_text_to_search = (job.job_title + " " + job.description_text + " " + jd_text).lower()
    
    if "angular" in full_text_to_search:
        passed_gates.append("CONTENT_ANGULAR")
    elif len(jd_text.strip()) < 200:
        # JD fetch failed or returned too little text — keep the job but flag it
        logger.warning(f"JD fetch insufficient ({len(jd_text)} chars) for {job.job_title} at {job.company_name}. Keeping as UNVERIFIED.")
        passed_gates.append("CONTENT_UNVERIFIED")
    else:
        # JD was fetched successfully but genuinely doesn't mention Angular — drop it
        logger.info(f"Dropped {job.job_title} at {job.company_name}: 'angular' not in {len(jd_text)}-char JD.")
        _log_drop(job.company_name, job.job_title, "CONTENT_ANGULAR", f"'angular' not found in {len(jd_text)}-char JD")
        return None

    # 4. Title-level negative stack filter
    # If the title explicitly names a non-Angular primary stack, drop it even
    # though the content check passed (the page may mention Angular elsewhere).
    title_lower = job.job_title.lower()
    has_negative = any(neg in title_lower for neg in NON_ANGULAR_TITLE_INDICATORS)
    has_angular_override = any(pos in title_lower for pos in ANGULAR_TITLE_OVERRIDES)

    if has_negative and not has_angular_override:
        _log_drop(job.company_name, job.job_title, "TITLE_STACK",
                  "Title indicates non-Angular primary stack")
        logger.info(f"Dropped {job.job_title} at {job.company_name}: title indicates non-Angular stack")
        return None
    passed_gates.append("TITLE_STACK")

    return FilteredJobListing(
        **job.model_dump(),
        passed_gates=passed_gates
    )
