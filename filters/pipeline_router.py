from typing import Optional
from schemas.job_listing import RawJobListing, FilteredJobListing, CompanyCategory
from config.geo_config import CATEGORY1_GEO_WHITELIST, CATEGORY2_GEO_WHITELIST
from filters.geo_filter import GeoFilter
from filters.title_filter import TitleFilter

def run_pipeline(job: RawJobListing) -> Optional[FilteredJobListing]:
    """Routes the job to the correct geographic filter based on its category."""
    passed_gates = []
    
    # Global Title Check: Ensure it's a tech role
    if not TitleFilter.passes(job.job_title):
        return None
    passed_gates.append("TITLE")
    
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

    return FilteredJobListing(
        **job.model_dump(),
        passed_gates=passed_gates
    )
