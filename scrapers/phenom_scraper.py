"""
Phenom API Scraper — tries multiple Phenom API endpoint patterns.

Phenom portals vary per tenant. Common patterns:
  GET /api/apply/v2/jobs?q=<query>&location=<loc>
  GET /api/jobs?q=<query>&location=<loc>
Response shape: { "jobs": [ { "title", "location", "jobUrl"|"applyUrl", ... } ] }

No browser. No LLM. Falls back gracefully if the API isn't available.
"""
import httpx
from typing import List, Dict, Any
from urllib.parse import urlparse
from schemas.job_listing import RawJobListing, CompanyCategory
from utils.text_normalizer import normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.phenom_api")


class PhenomAPIScraper:
    """API-first scraper for Phenom-powered career portals."""

    async def scrape(self, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        """Try Phenom API endpoints. Returns empty list if no API is found."""
        parsed = urlparse(company["url"])
        base = f"{parsed.scheme}://{parsed.netloc}"

        # Common Phenom API endpoints to try
        api_paths = [
            "/api/apply/v2/jobs",
            "/api/jobs",
            "/wps/portal/api/v1.0/jobs",
        ]

        for api_path in api_paths:
            api_url = f"{base}{api_path}"
            try:
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    params = {"q": "Angular", "location": "India", "limit": "100"}
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "application/json",
                    }
                    response = await client.get(api_url, params=params, headers=headers)

                    if response.status_code != 200:
                        continue

                    data = response.json()
                    api_jobs = data.get("jobs", [])
                    if not api_jobs:
                        continue

                    logger.info(f"Phenom API ({api_path}) returned {len(api_jobs)} jobs for {company['name']}")
                    jobs = []
                    for j in api_jobs:
                        job_url = j.get("jobUrl") or j.get("applyUrl") or j.get("url", "")
                        if job_url and not job_url.startswith("http"):
                            job_url = f"{base}{job_url}"

                        jd_text = j.get("description", j.get("title", ""))[:2000]

                        jobs.append(
                            RawJobListing(
                                company_name=company["name"],
                                company_tier=company["tier"],
                                category=category,
                                job_title=j.get("title", "Unknown"),
                                location=normalize_location(j.get("location", "Unknown")),
                                description_text=jd_text,
                                application_url=job_url or company["url"],
                            )
                        )
                    return jobs

            except Exception as e:
                logger.debug(f"Phenom API attempt failed ({api_path}): {e}")
                continue

        logger.warning(f"No Phenom API endpoints worked for {company['name']}")
        return None
