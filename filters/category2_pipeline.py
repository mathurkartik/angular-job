from typing import Optional
from schemas.job_listing import RawJobListing, FilteredJobListing
from config.geo_config import CATEGORY2_GEO_WHITELIST
from config.seniority_config import CATEGORY2_SENIORITY_PATTERNS
from filters.geo_filter import GeoFilter
from filters.seniority_filter import SeniorityFilter
from filters.stack_filter import StackFilter

class Category2Pipeline:
    """
    Relaxed pipeline for Indian Product Companies.
    Must pass Geo (relaxed), Seniority (relaxed), and Stack filters.
    """
    @staticmethod
    def process(job: RawJobListing) -> Optional[FilteredJobListing]:
        passed_gates = []
        
        if not GeoFilter.passes(job.location, CATEGORY2_GEO_WHITELIST):
            return None
        passed_gates.append("GEO_RELAXED")
        
        combined_text = f"{job.job_title} {job.description_text}"
        if not SeniorityFilter.passes(combined_text, CATEGORY2_SENIORITY_PATTERNS):
            return None
        passed_gates.append("SENIORITY_RELAXED")
        
        if not StackFilter.passes(combined_text):
            return None
        passed_gates.append("STACK")
        
        return FilteredJobListing(
            **job.model_dump(),
            passed_gates=passed_gates
        )
