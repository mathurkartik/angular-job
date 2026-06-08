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
    company_tier: str                      # e.g., "Tier_1_Domain_Match"
    category: CompanyCategory              # Which of the 3 categories
    job_title: str
    location: str
    description_text: str                  # Full JD text (cleaned)
    application_url: HttpUrl
    date_posted: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)

class FilteredJobListing(RawJobListing):
    """A listing that passed its category-specific filter pipeline."""
    passed_gates: List[str]                # Which gates it cleared

class ScoredJobListing(FilteredJobListing):
    """A listing with semantic scoring applied."""
    total_score: float                     # 0.0 – 1.0
    pillar_scores: Dict[str, float]        # Per-pillar breakdown
    matched_keywords: Dict[str, List[str]] # Keywords hit per pillar
    justification: str                     # "Why It Matches" summary
    rank: Optional[int] = None             # Priority rank within its category
