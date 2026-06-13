"""Workday API Scraper — uses the internal cxs JSON endpoint with pagination."""
import httpx, re
from typing import List, Dict, Any, Optional, Tuple
from schemas.job_listing import RawJobListing, CompanyCategory
from utils.text_normalizer import normalize_location
from utils.logger import get_logger

logger = get_logger("scraper.workday_api")


def _parse_workday_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    From a Workday careers URL, derive the cxs API endpoint.
    e.g. https://citi.wd5.myworkdayjobs.com/en-US/2 →
         host=citi.wd5.myworkdayjobs.com, tenant=citi, site=2
    Returns (api_endpoint, base_for_apply_links) or (None, None) if unparseable.
    """
    m = re.match(r"https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/(?:([^/]+)/)?([^/?]+)", url)
    if not m:
        return None, None
    tenant, wd, lang, site = m.groups()
    host = f"{tenant}.{wd}.myworkdayjobs.com"
    api = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    apply_base = f"https://{host}/{lang or 'en-US'}/{site}"
    return api, apply_base


class WorkdayAPIScraper:
    async def scrape(self, company: Dict[str, Any], category: CompanyCategory) -> List[RawJobListing]:
        api, apply_base = _parse_workday_url(company["url"])
        if not api:
            logger.warning(f"Could not parse Workday URL for {company['name']}: {company['url']}")
            return []

        jobs = []
        offset, limit = 0, 20
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                while True:
                    body = {"appliedFacets": {}, "limit": limit, "offset": offset, "searchText": "Angular"}
                    resp = await client.post(api, json=body, headers=headers)
                    if resp.status_code != 200:
                        logger.warning(f"Workday API {resp.status_code} for {company['name']}")
                        if offset == 0:
                            return None
                        break
                    data = resp.json()
                    postings = data.get("jobPostings", [])
                    for j in postings:
                        ext = j.get("externalPath", "")
                        apply_url = f"{apply_base}{ext}" if ext else company["url"]
                        jobs.append(RawJobListing(
                            company_name=company["name"],
                            company_tier=company["tier"],
                            category=category,
                            job_title=j.get("title", "Unknown"),
                            location=normalize_location(j.get("locationsText", "Unknown")),
                            description_text=j.get("title", ""),  # Workday list view has no JD
                            application_url=apply_url,
                        ))
                    total = data.get("total", 0)
                    offset += limit
                    if offset >= total or not postings:
                        break
                logger.info(f"Workday API returned {len(jobs)} jobs for {company['name']}")
        except Exception as e:
            logger.error(f"Workday API error for {company['name']}: {e}")
            return None
        return jobs
