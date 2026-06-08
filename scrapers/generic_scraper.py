from typing import List, Dict, Any
from playwright.async_api import Page
from bs4 import BeautifulSoup
from schemas.job_listing import RawJobListing, CompanyCategory
from scrapers.base_scraper import BaseScraper
from utils.text_normalizer import clean_html, normalize_location

class GenericScraper(BaseScraper):
    """
    Fallback scraper for custom-built career portals.
    Uses generic heuristics to find "Job" cards and extract text.
    """

    async def extract_jobs(self, page: Page, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        # Scroll to load lazy content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)  # wait for network requests

        # Extract full HTML
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        jobs = []
        
        # Heuristic 1: Look for common job card classes or tags
        # This is very generic; in reality, complex generic scrapers might need LLMs or specific CSS paths.
        # We will extract ALL links that might be a job.
        
        links = soup.find_all("a", href=True)
        for link in links:
            text = clean_html(link.get_text())
            href = link["href"]
            
            if not href.startswith("http"):
                # Handle relative URLs (simplified)
                base_domain = company["url"].rstrip("/")
                href = f"{base_domain}{href}" if href.startswith("/") else f"{base_domain}/{href}"

            # If it mentions angular or senior, log it (rudimentary pre-filter for generics)
            if "angular" in text.lower() or "frontend" in text.lower():
                # Get the parent text as the "description" to run deeper filters later
                parent_text = clean_html(link.parent.get_text()) if link.parent else text
                
                jobs.append(
                    RawJobListing(
                        company_name=company["name"],
                        company_tier=company["tier"],
                        category=category,
                        job_title=text[:100],  # Guessing link text is title
                        location="Unknown",    # Generic can't easily parse location
                        description_text=parent_text,
                        application_url=href
                    )
                )

        return jobs
