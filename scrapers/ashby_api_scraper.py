"""Ashby API Scraper — public JSON API, no browser, no LLM."""
import httpx
from typing import List, Dict, Any
from urllib.parse import urlparse
from schemas.job_listing import RawJobListing, CompanyCategory
from utils.text_normalizer import normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.ashby_api")


def _extract_ashby_org(url: str) -> str:
    """From https://jobs.ashbyhq.com/orgname → 'orgname'."""
    path = url.split("?")[0].rstrip("/")
    return path.split("/")[-1]


class AshbyAPIScraper:
    async def scrape(self, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        org = _extract_ashby_org(company["url"])
        api_url = f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=false"
        logger.info(f"Fetching Ashby API: {api_url}")

        jobs = []
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(api_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                if resp.status_code != 200:
                    logger.warning(f"Ashby API {resp.status_code} for {company['name']}")
                    return None
                data = resp.json()
                api_jobs = data.get("jobs", [])
                for j in api_jobs:
                    jd_text = j.get("descriptionPlain", "")[:2000]
                    jobs.append(RawJobListing(
                        company_name=company["name"],
                        company_tier=company["tier"],
                        category=category,
                        job_title=j.get("title", "Unknown"),
                        location=normalize_location(j.get("location", "Unknown")),
                        description_text=jd_text,
                        application_url=j.get("jobUrl", company["url"]),
                    ))
                logger.info(f"Ashby API returned {len(jobs)} jobs for {company['name']}")
        except Exception as e:
            logger.error(f"Ashby API error for {company['name']}: {e}")
            return None
        return jobs
