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
            # Wait for initial load
            await page.wait_for_selector("ul[data-automation-id='jobResults'] li", timeout=15000)
        except Exception as e:
            logger.warning(f"Could not find Workday job results container for {company['name']}")
            return jobs

        max_pages = 5
        for current_page in range(max_pages):
            logger.info(f"Scraping Workday page {current_page + 1} for {company['name']}")
            
            # Extract jobs from current page
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            job_elements = soup.select("ul[data-automation-id='jobResults'] li")
            
            for element in job_elements:
                title_tag = element.find("a", attrs={"data-automation-id": "jobTitle"})
                if not title_tag:
                    continue
                    
                title = clean_html(title_tag.get_text())
                href = title_tag.get("href")
                
                if href.startswith("/"):
                    base_url = "/".join(company["url"].split("/")[:3])
                    full_url = f"{base_url}{href}"
                else:
                    full_url = href
                    
                location_tag = element.find("dd", attrs={"class": "css-129m7dg"}) 
                location = "Unknown"
                if location_tag:
                    location = clean_html(location_tag.get_text())
                
                jobs.append(
                    RawJobListing(
                        company_name=company["name"],
                        company_tier=company["tier"],
                        category=category,
                        job_title=title,
                        location=normalize_location(location),
                        description_text=title,
                        application_url=full_url
                    )
                )
            
            # Try to click the Next button
            try:
                next_button = await page.query_selector("button[aria-label='next']")
                if next_button and await next_button.is_enabled():
                    await next_button.click()
                    await page.wait_for_timeout(3000) # Give it time to load the next page
                    await page.wait_for_selector("ul[data-automation-id='jobResults'] li", timeout=10000)
                else:
                    break # No more pages
            except Exception as e:
                logger.debug(f"Pagination stopped for {company['name']}: {e}")
                break

        return jobs
