"""
Greenhouse API Scraper — uses the public JSON API instead of browser scraping.

API docs: https://developers.greenhouse.io/job-board.html
Endpoint: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true

Returns all jobs with full HTML description. No auth, no browser, no rate limits.
"""

import httpx
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from schemas.job_listing import RawJobListing, CompanyCategory
from utils.text_normalizer import clean_html, normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.greenhouse_api")


def _extract_board_token(url: str) -> str:
    """
    Extract the Greenhouse board token from various URL formats:
    - https://boards.greenhouse.io/companyname
    - https://job-boards.greenhouse.io/companyname
    - https://boards.eu.greenhouse.io/companyname
    - https://job-boards.eu.greenhouse.io/companyname
    """
    # Remove query params and trailing slashes
    path = url.split("?")[0].rstrip("/")
    # The board token is the last path segment
    return path.split("/")[-1]


class GreenhouseAPIScraper:
    """
    Fetches jobs from Greenhouse's public Job Board API.
    No browser needed — plain HTTP GET returning JSON.
    """

    async def scrape(self, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        board_token = _extract_board_token(company["url"])
        url = company["url"]

        # Determine the correct API base (EU vs US)
        if ".eu.greenhouse.io" in url:
            api_base = "https://boards-api.eu.greenhouse.io/v1/boards"
        else:
            api_base = "https://boards-api.greenhouse.io/v1/boards"

        api_url = f"{api_base}/{board_token}/jobs?content=true"
        logger.info(f"Fetching Greenhouse API: {api_url}")

        jobs = []
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                }
                response = await client.get(api_url, headers=headers)

                if response.status_code != 200:
                    logger.warning(f"Greenhouse API returned {response.status_code} for {company['name']}")
                    return None

                data = response.json()
                api_jobs = data.get("jobs", [])
                logger.info(f"Greenhouse API returned {len(api_jobs)} jobs for {company['name']}")

                for job_data in api_jobs:
                    title = job_data.get("title", "Unknown")

                    # Extract location from the structured location object
                    location_name = job_data.get("location", {}).get("name", "Unknown")

                    # The job URL
                    job_url = job_data.get("absolute_url", "")
                    if not job_url:
                        job_id = job_data.get("id", "")
                        job_url = f"https://boards.greenhouse.io/{board_token}/jobs/{job_id}"

                    # Extract description text (HTML) — clean it for content filtering
                    content_html = job_data.get("content", "")
                    description_text = ""
                    if content_html:
                        soup = BeautifulSoup(content_html, "html.parser")
                        description_text = soup.get_text(separator=" ", strip=True)[:2000]

                    jobs.append(
                        RawJobListing(
                            company_name=company["name"],
                            company_tier=company["tier"],
                            category=category,
                            job_title=title,
                            location=normalize_location(location_name),
                            description_text=description_text,
                            application_url=job_url,
                        )
                    )

        except Exception as e:
            logger.error(f"Greenhouse API error for {company['name']}: {str(e)}")
            return None

        return jobs
