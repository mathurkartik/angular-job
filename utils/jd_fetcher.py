import httpx
from bs4 import BeautifulSoup
from utils.logger import get_logger
from playwright.async_api import async_playwright
import asyncio

logger = get_logger("jd_fetcher")

async def fetch_jd_text(url: str) -> str:
    """
    Fetches the raw text from a job description URL.
    Returns the lowercased text for easy keyword matching.
    """
    text = ""
    try:
        # Use a timeout of 15 seconds to avoid hanging on bad pages
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            response = await client.get(str(url), headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Extract text, removing script/style tags
                for element in soup(["script", "style"]):
                    element.extract()
                text = soup.get_text(separator=" ", strip=True).lower()
            else:
                logger.warning(f"Failed to fetch JD {url}: HTTP {response.status_code}")
    except Exception as e:
        logger.warning(f"Error fetching JD {url} via httpx: {str(e)}")

    # Fallback to Playwright if text is too short (SPA portals like Phenom/Workday)
    if len(text) < 500:
        logger.info(f"Text too short ({len(text)} chars), falling back to Playwright for {url}")
        text = await _fetch_jd_playwright(str(url))

    return text

async def _fetch_jd_playwright(url: str) -> str:
    """Fallback method to extract text from SPA sites using Playwright and Stealth."""
    from scrapers.base_scraper import BaseScraper
    
    try:
        # Create a dummy company dict to satisfy BaseScraper
        company = {"name": "JD Fetch", "url": url}
        scraper = BaseScraper(headless=True)
        text = await scraper.get_page_text(company)
        return text.lower() if text else ""
    except Exception as e:
        logger.warning(f"Playwright fallback failed for {url}: {str(e)}")
        return ""

