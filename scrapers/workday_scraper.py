from typing import List, Dict, Any
from playwright.async_api import Page
from bs4 import BeautifulSoup

from schemas.job_listing import RawJobListing, CompanyCategory
from scrapers.base_scraper import BaseScraper
from utils.text_normalizer import clean_html, normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.workday")

class WorkdayScraper(BaseScraper):
    """
    Scraper for Workday career portals.
    Waits for the job list container to render, then parses it.
    """

    async def extract_jobs(self, page: Page, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        jobs = []
        
        try:
            # Workday typically uses a generic class for job items, e.g., 'css-1q2dra3' or ul elements.
            # We'll wait for the main list or wait for network idle to ensure React renders the list.
            await page.wait_for_selector("ul[data-automation-id='jobResults'] li", timeout=15000)
        except Exception as e:
            logger.warning(f"Could not find Workday job results container for {company['name']}")
            return jobs

        # Expand pagination if needed (basic loop)
        # For simplicity in this implementation, we just grab the first page
        
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        job_elements = soup.select("ul[data-automation-id='jobResults'] li")
        
        for element in job_elements:
            # Extract Title and URL
            title_tag = element.find("a", attrs={"data-automation-id": "jobTitle"})
            if not title_tag:
                continue
                
            title = clean_html(title_tag.get_text())
            href = title_tag.get("href")
            
            # Form full URL
            if href.startswith("/"):
                base_url = "/".join(company["url"].split("/")[:3]) # e.g. https://xyz.wd1.myworkdayjobs.com
                full_url = f"{base_url}{href}"
            else:
                full_url = href
                
            # Extract location
            location_tag = element.find("dd", attrs={"class": "css-129m7dg"}) # Often contains location in some workday builds
            # Alternatively look for the string near location icon
            location = "Unknown"
            if location_tag:
                location = clean_html(location_tag.get_text())
            
            # Since Workday requires clicking into the job to see the full JD,
            # we will record the short description available or just the title.
            # In a full deep-crawl architecture, we would queue these URLs for individual scraping.
            # For this MVP phase, we just extract the snippet.
            
            jobs.append(
                RawJobListing(
                    company_name=company["name"],
                    company_tier=company["tier"],
                    category=category,
                    job_title=title,
                    location=normalize_location(location),
                    description_text=title, # Storing title as desc placeholder if snippet unavailable
                    application_url=full_url
                )
            )

        return jobs
