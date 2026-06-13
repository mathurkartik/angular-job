"""SmartRecruiters API Scraper — public JSON API, no browser, no LLM."""
import httpx
from typing import List, Dict, Any
from urllib.parse import urlparse
from schemas.job_listing import RawJobListing, CompanyCategory
from utils.text_normalizer import normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.smartrecruiters_api")


def _extract_company_id(url: str) -> str:
    """From https://careers.smartrecruiters.com/CompanyName → 'CompanyName'."""
    path = url.split("?")[0].rstrip("/")
    return path.split("/")[-1]


class SmartRecruitersAPIScraper:
    async def scrape(self, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        company_id = _extract_company_id(company["url"])
        api_url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
        logger.info(f"Fetching SmartRecruiters API: {api_url}")

        jobs = []
        offset = 0
        limit = 100
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                while True:
                    params = {"q": "Angular", "limit": limit, "offset": offset}
                    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
                    resp = await client.get(api_url, params=params, headers=headers)
                    if resp.status_code != 200:
                        logger.warning(f"SmartRecruiters API {resp.status_code} for {company['name']}")
                        if offset == 0:
                            return None
                        break

                    data = resp.json()
                    postings = data.get("content", [])
                    if not postings:
                        break

                    for j in postings:
                        posting_id = j.get("id", "")
                        location_obj = j.get("location", {})
                        city = location_obj.get("city", "")
                        country = location_obj.get("country", "")
                        location = f"{city}, {country}".strip(", ") if city or country else "Unknown"

                        apply_url = f"https://jobs.smartrecruiters.com/{company_id}/{posting_id}"

                        # Try to get description from customField or name
                        jd_text = j.get("name", "")[:2000]

                        jobs.append(RawJobListing(
                            company_name=company["name"],
                            company_tier=company["tier"],
                            category=category,
                            job_title=j.get("name", "Unknown"),
                            location=normalize_location(location),
                            description_text=jd_text,
                            application_url=apply_url,
                        ))

                    # SmartRecruiters uses totalFound for pagination
                    total = data.get("totalFound", len(postings))
                    offset += limit
                    if offset >= total:
                        break

                logger.info(f"SmartRecruiters API returned {len(jobs)} jobs for {company['name']}")
        except Exception as e:
            logger.error(f"SmartRecruiters API error for {company['name']}: {e}")
            return None
        return jobs
