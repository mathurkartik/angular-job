from typing import Optional
from schemas.job_listing import RawJobListing, FilteredJobListing
from filters.stack_filter import StackFilter

class Category3Pipeline:
    """
    Minimal pipeline for Service-based companies (Market Intel).
    Only requires Stack filter. Geo and Seniority are ignored.
    """
    @staticmethod
    def process(job: RawJobListing) -> Optional[FilteredJobListing]:
        passed_gates = []
        
        combined_text = f"{job.job_title} {job.description_text}"
        
        if not StackFilter.passes(combined_text):
            return None
        passed_gates.append("STACK")
        passed_gates.append("GEO_BYPASSED")
        passed_gates.append("SENIORITY_BYPASSED")
        
        return FilteredJobListing(
            **job.model_dump(),
            passed_gates=passed_gates
        )
