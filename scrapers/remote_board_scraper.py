from typing import List, Dict, Any
from playwright.async_api import Page
from bs4 import BeautifulSoup

from schemas.job_listing import RawJobListing, CompanyCategory
from scrapers.base_scraper import BaseScraper
from utils.text_normalizer import clean_html, normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.remote_board")

class RemoteBoardScraper(BaseScraper):
    """
    Scraper for Global Remote Boards (WeWorkRemotely, RemoteOK).
    """

    async def extract_jobs(self, page: Page, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        # For remote boards, we just use the generic heuristic for now
        # Ideally, we would have specific parsers for WWR and RemoteOK
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

            if "angular" in text.lower() or "frontend" in text.lower() or "front-end" in text.lower():
                jobs.append(
                    RawJobListing(
                        company_name=company["name"],
                        company_tier=company["tier"],
                        category=category,
                        job_title=text[:100],
                        location="remote",  # By definition
                        description_text=text,
                        application_url=href
                    )
                )

        return jobs
