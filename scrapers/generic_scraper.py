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

        # Extract inner text instead of HTML for LLM parsing
        page_text = await page.evaluate("document.body.innerText")
        
        jobs = []
        
        # Call Groq to extract the jobs
        from utils.groq_client import groq_client
        extracted_data = groq_client.extract_jobs_from_text(page_text, company["url"])
        
        raw_jobs_list = extracted_data.get("jobs", []) if isinstance(extracted_data, dict) else []
        
        for job_data in raw_jobs_list:
            jobs.append(
                RawJobListing(
                    company_name=company["name"],
                    company_tier=company["tier"],
                    category=category,
                    job_title=job_data.get("job_title", "Unknown"),
                    location=job_data.get("location", "Unknown"),
                    description_text=job_data.get("description_text", ""),
                    application_url=job_data.get("application_url", company["url"])
                )
            )

        return jobs
