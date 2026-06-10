from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class CompanyCategory(str, Enum):
    MAIN = "main"
    INDIAN_PRODUCT = "indian_product"
    SERVICE = "service"

class RawJobListing(BaseModel):
    """Raw data extracted directly from a career page."""
    company_name: str
    company_tier: str                      # e.g., "Tier_1_Global_GCC"
    category: CompanyCategory              # Which of the 3 categories
    job_title: str
    location: str
    description_text: str                  # Full JD text (cleaned)
    application_url: HttpUrl
    date_posted: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)

class ReviewedJobListing(RawJobListing):
    """A listing that has been reviewed by the Extraction Reviewer (Agent 2)."""
    extraction_verified: bool = True       # Agent 2 confirmed this is real
    reviewer_notes: str = ""               # Agent 2's notes (e.g., "URL corrected")

class FilteredJobListing(ReviewedJobListing):
    """A listing that passed its category-specific filter pipeline."""
    passed_gates: List[str] = Field(default_factory=list)

class ExportedJobListing(FilteredJobListing):
    """Final listing format exported to JSON/CSV."""
    rank: Optional[int] = None             # Priority rank within its category
