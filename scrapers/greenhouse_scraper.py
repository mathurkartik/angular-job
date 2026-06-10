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
            # Try waiting for either of the common Greenhouse job containers
            await page.wait_for_selector("div.opening, tr.job-post", timeout=15000)
        except Exception:
            logger.warning(f"Could not find Greenhouse job results container for {company['name']}")
            return jobs

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Select both possible job row containers
        job_elements = soup.select("div.opening, tr.job-post")
        
        for element in job_elements:
            title_tag = element.find("a")
            if not title_tag:
                continue
                
            href = title_tag.get("href")
            
            # Check if it's the tr.job-post template (OneTrust)
            if "job-post" in element.get("class", []):
                title_p = element.find("p", class_="body--medium")
                location_p = element.find("p", class_="body__secondary")
                title = clean_html(title_p.get_text()) if title_p else "Unknown"
                location_text = clean_html(location_p.get_text()) if location_p else "Unknown"
            else:
                # Standard div.opening template
                title = clean_html(title_tag.get_text())
                location_span = element.find("span", attrs={"class": "location"})
                location_text = clean_html(location_span.get_text()) if location_span else "Unknown"
            
            if href.startswith("/"):
                base_url = "https://boards.greenhouse.io"
                full_url = f"{base_url}{href}"
            else:
                full_url = href
                
            jobs.append(
                RawJobListing(
                    company_name=company["name"],
                    company_tier=company["tier"],
                    category=category,
                    job_title=title,
                    location=normalize_location(location_text),
                    description_text=title, # Full JD requires deep crawl
                    application_url=full_url
                )
            )

        return jobs
