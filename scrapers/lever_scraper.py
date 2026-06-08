from typing import List, Dict, Any
from playwright.async_api import Page
from bs4 import BeautifulSoup

from schemas.job_listing import RawJobListing, CompanyCategory
from scrapers.base_scraper import BaseScraper
from utils.text_normalizer import clean_html, normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.lever")

class LeverScraper(BaseScraper):
    """
    Scraper for Lever career portals.
    """

    async def extract_jobs(self, page: Page, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        jobs = []
        
        try:
            # Lever usually renders job items in <div class="posting">
            await page.wait_for_selector("div.posting", timeout=15000)
        except Exception:
            logger.warning(f"Could not find Lever job results container for {company['name']}")
            return jobs

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        job_elements = soup.select("div.posting")
        
        for element in job_elements:
            title_tag = element.find("h5", attrs={"data-qa": "posting-name"})
            if not title_tag:
                continue
                
            title = clean_html(title_tag.get_text())
            
            # Link is usually on the parent `a.posting-title`
            link_tag = element.find("a", attrs={"class": "posting-title"})
            href = link_tag.get("href") if link_tag else ""
            
            location_tag = element.find("span", attrs={"class": "sort-by-location"})
            location = clean_html(location_tag.get_text()) if location_tag else "Unknown"
            
            jobs.append(
                RawJobListing(
                    company_name=company["name"],
                    company_tier=company["tier"],
                    category=category,
                    job_title=title,
                    location=normalize_location(location),
                    description_text=title, 
                    application_url=href
                )
            )

        return jobs
