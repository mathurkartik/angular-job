from typing import List, Dict, Any
from playwright.async_api import Page
from bs4 import BeautifulSoup

from schemas.job_listing import RawJobListing, CompanyCategory
from scrapers.base_scraper import BaseScraper
from utils.text_normalizer import clean_html, normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.talent_network")

class TalentNetworkScraper(BaseScraper):
    """
    Scraper for Global Talent Networks (Toptal, Turing, Andela).
    """

    async def extract_jobs(self, page: Page, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        # Talent networks often require sign-up. 
        # This is a stub for extracting public role listings where available.
        # Uses the generic heuristic.
        
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        jobs = []
        links = soup.find_all("a", href=True)
        for link in links:
            text = clean_html(link.get_text())
            href = link["href"]
            
            if not href.startswith("http"):
                base_domain = "/".join(company["url"].split("/")[:3])
                href = f"{base_domain}{href}" if href.startswith("/") else f"{base_domain}/{href}"

            if "angular" in text.lower() or "frontend" in text.lower() or "developer" in text.lower():
                jobs.append(
                    RawJobListing(
                        company_name=company["name"],
                        company_tier=company["tier"],
                        category=category,
                        job_title=text[:100],
                        location="remote",
                        description_text=text,
                        application_url=href
                    )
                )

        return jobs
