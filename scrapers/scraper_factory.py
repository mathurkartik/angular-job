"""
Scraper Factory — routes companies to the correct API scraper.

API scrapers (no browser, no LLM):
  greenhouse, lever, workday, smartrecruiters, ashby, phenom

Everything else -> GenericScraper (browser + LLM fallback)
"""
from scrapers.generic_scraper import GenericScraper
from scrapers.greenhouse_api_scraper import GreenhouseAPIScraper
from scrapers.lever_api_scraper import LeverAPIScraper
from scrapers.workday_api_scraper import WorkdayAPIScraper
from scrapers.smartrecruiters_api_scraper import SmartRecruitersAPIScraper
from scrapers.ashby_api_scraper import AshbyAPIScraper
from scrapers.phenom_scraper import PhenomAPIScraper

# Map of ATS types to their API-only scraper classes
_API_SCRAPERS = {
    "greenhouse": GreenhouseAPIScraper,
    "lever": LeverAPIScraper,
    "workday": WorkdayAPIScraper,
    "smartrecruiters": SmartRecruitersAPIScraper,
    "ashby": AshbyAPIScraper,
    "phenom": PhenomAPIScraper,
}


def get_scraper(portal_type: str, headless: bool = True):
    """
    Factory method to instantiate the correct scraper based on portal type.
    Returns an API scraper (no browser) if available, else GenericScraper.
    """
    if portal_type in _API_SCRAPERS:
        return _API_SCRAPERS[portal_type]()  # no browser needed
    # Everything else → browser + LLM fallback
    return GenericScraper(headless=headless)


def is_api_scraper(portal_type: str) -> bool:
    """Check if the portal type has a dedicated API scraper."""
    return portal_type in _API_SCRAPERS
