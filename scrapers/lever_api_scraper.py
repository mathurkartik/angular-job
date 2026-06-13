"""Lever API Scraper — public JSON API, no browser, no LLM."""
import httpx
from typing import List, Dict, Any
from urllib.parse import urlparse
from schemas.job_listing import RawJobListing, CompanyCategory
from utils.text_normalizer import normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.lever_api")


def _extract_lever_token(url: str) -> str:
    """From https://jobs.lever.co/companyname → 'companyname'."""
    path = url.split("?")[0].rstrip("/")
    return path.split("/")[-1]


class LeverAPIScraper:
    async def scrape(self, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        token = _extract_lever_token(company["url"])
        api_url = f"https://api.lever.co/v0/postings/{token}?mode=json"
        logger.info(f"Fetching Lever API: {api_url}")

        jobs = []
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(api_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                if resp.status_code != 200:
                    logger.warning(f"Lever API {resp.status_code} for {company['name']}")
                    return None
                for j in resp.json():
                    location = j.get("categories", {}).get("location", "Unknown")
                    jd_text = j.get("descriptionPlain", "")[:2000]
                    jobs.append(RawJobListing(
                        company_name=company["name"],
                        company_tier=company["tier"],
                        category=category,
                        job_title=j.get("text", "Unknown"),
                        location=normalize_location(location),
                        description_text=jd_text,
                        application_url=j.get("hostedUrl", company["url"]),
                    ))
                logger.info(f"Lever API returned {len(jobs)} jobs for {company['name']}")
        except Exception as e:
            logger.error(f"Lever API error for {company['name']}: {e}")
            return None
        return jobs
