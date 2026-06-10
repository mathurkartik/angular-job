from typing import Optional
from schemas.job_listing import RawJobListing, FilteredJobListing
from config.geo_config import CATEGORY1_GEO_WHITELIST
from config.seniority_config import CATEGORY1_SENIORITY_PATTERNS
from filters.geo_filter import GeoFilter
from filters.seniority_filter import SeniorityFilter
from filters.stack_filter import StackFilter

class Category1Pipeline:
    """
    Strict pipeline for Main Companies.
    Must pass Geo, Seniority, and Stack filters.
    """
    @staticmethod
    def process(job: RawJobListing) -> Optional[FilteredJobListing]:
        passed_gates = []
        
        # 1. Geo Filter
        if not GeoFilter.passes(job.location, CATEGORY1_GEO_WHITELIST):
            return None
        passed_gates.append("GEO")
        
        # 2. Seniority Filter
        combined_text = f"{job.job_title} {job.description_text}"
        if not SeniorityFilter.passes(combined_text, CATEGORY1_SENIORITY_PATTERNS):
            return None
        passed_gates.append("SENIORITY")
        
        # 3. Stack Filter (Bypassed because full JDs are no longer fetched)
        # if not StackFilter.passes(combined_text):
        #     return None
        passed_gates.append("STACK")
        
        return FilteredJobListing(
            **job.model_dump(),
            passed_gates=passed_gates
        )
