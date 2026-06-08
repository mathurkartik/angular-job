from typing import Optional
from schemas.job_listing import RawJobListing, FilteredJobListing, CompanyCategory
from filters.category1_pipeline import Category1Pipeline
from filters.category2_pipeline import Category2Pipeline
from filters.category3_pipeline import Category3Pipeline

def run_pipeline(job: RawJobListing) -> Optional[FilteredJobListing]:
    """Routes the job to the correct pipeline based on its category."""
    if job.category == CompanyCategory.MAIN:
        return Category1Pipeline.process(job)
    elif job.category == CompanyCategory.INDIAN_PRODUCT:
        return Category2Pipeline.process(job)
    elif job.category == CompanyCategory.SERVICE:
        return Category3Pipeline.process(job)
    else:
        # Fallback to strict
        return Category1Pipeline.process(job)
