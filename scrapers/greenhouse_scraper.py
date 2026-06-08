from typing import List, Dict, Any
from playwright.async_api import Page
from bs4 import BeautifulSoup

from schemas.job_listing import RawJobListing, CompanyCategory
from scrapers.base_scraper import BaseScraper
from utils.text_normalizer import clean_html, normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.greenhouse")

class GreenhouseScraper(BaseScraper):
    """
    Scraper for Greenhouse career portals.
    """

    async def extract_jobs(self, page: Page, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        jobs = []
        
        try:
            # Greenhouse usually renders job items in <div class="opening">
            await page.wait_for_selector("div.opening", timeout=15000)
        except Exception:
            logger.warning(f"Could not find Greenhouse job results container for {company['name']}")
            return jobs

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        job_elements = soup.select("div.opening")
        
        for element in job_elements:
            title_tag = element.find("a")
            if not title_tag:
                continue
                
            title = clean_html(title_tag.get_text())
            href = title_tag.get("href")
            
            if href.startswith("/"):
                base_url = "https://boards.greenhouse.io"
                full_url = f"{base_url}{href}"
            else:
                full_url = href
                
            location_tag = element.find("span", attrs={"class": "location"})
            location = clean_html(location_tag.get_text()) if location_tag else "Unknown"
            
            jobs.append(
                RawJobListing(
                    company_name=company["name"],
                    company_tier=company["tier"],
                    category=category,
                    job_title=title,
                    location=normalize_location(location),
                    description_text=title, # Full JD requires deep crawl
                    application_url=full_url
                )
            )

        return jobs
