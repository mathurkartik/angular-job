import asyncio
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth

from schemas.job_listing import RawJobListing, CompanyCategory
from stealth.identity_rotator import get_random_identity
from stealth.pacing import pacing_manager
from utils.logger import get_logger

logger = get_logger("scraper.base")

class BaseScraper:
    """
    Abstract base class for all portal-specific scrapers.
    Handles browser orchestration, stealth injection, and pacing.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def init_browser(self):
        """Initializes Playwright with stealth configurations."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        identity = get_random_identity()
        self.context = await self.browser.new_context(
            user_agent=identity["user_agent"],
            viewport=identity["viewport"],
            locale=identity["locale"],
            color_scheme=identity["color_scheme"]
        )

        self.page = await self.context.new_page()
        # Apply playwright-stealth to bypass bot detection (Cloudflare/Datadome)
        await Stealth().apply_stealth_async(self.page)

    async def close_browser(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape(self, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        """
        Main entry point for scraping. 
        Child classes MUST implement `extract_jobs`.
        """
        url = company["url"]
        logger.info(f"Scraping [{company['name']}] at {url}...")
        
        # Enforce pacing
        await pacing_manager.apply_delay(url)

        try:
            await self.init_browser()
            
            # Navigate with network idle wait
            response = await self.page.goto(url, wait_until="networkidle", timeout=45000)
            
            if response and response.status in [403, 429]:
                logger.warning(f"Access blocked (Status {response.status}) for {company['name']}")
                pacing_manager.record_failure(url)
                return []
            
            pacing_manager.record_success(url)
            
            # Delegate to subclass for actual DOM parsing
            jobs = await self.extract_jobs(self.page, company, category)
            logger.info(f"Extracted {len(jobs)} potential listings from {company['name']}.")
            return jobs

        except Exception as e:
            logger.error(f"Failed to scrape {company['name']}: {str(e)}")
            pacing_manager.record_failure(url)
            return []
            
        finally:
            await self.close_browser()

    async def extract_jobs(self, page: Page, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        """
        MUST be implemented by subclasses.
        Should extract job details from the page and return a list of RawJobListings.
        """
        raise NotImplementedError("Subclasses must implement `extract_jobs`.")
