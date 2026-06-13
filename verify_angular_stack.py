"""
verify_angular_stack.py — One-time audit of all companies for Angular relevance.
Run this before rebuilding the company configs. Outputs a CSV report.
"""
import asyncio, csv, httpx, json, re
from config.companies_main import COMPANIES as main_companies
from config.companies_indian_product import COMPANIES as product_companies
from config.companies_service import COMPANIES as service_companies

OUTPUT = "output/company_stack_audit.csv"

NON_ANGULAR_TITLE_INDICATORS = [
    ".net", "dotnet", "c#", "csharp",
    "java developer", "java engineer", "fullstack java", "full stack java",
    "python developer", "python engineer", "data engineer", "data quality",
    "ruby", "golang", "go developer",
    "openwrt", "rdk", "linux platform",
    "design engineer", "network engineer",
    "embedded", "firmware", "hardware",
    "backend developer", "back-end developer",
    "application support", "production support",
    "sre", "site reliability", "devops",
    "qa", "sdet", "test engineer",
    "aem",  # Adobe Experience Manager, not Angular
]

ANGULAR_TITLE_OVERRIDES = ["angular", "frontend", "front-end", "front end", "ui engineer", "ui developer"]

def is_likely_angular_role(title: str) -> bool:
    """Check if the job title suggests an Angular-relevant role."""
    t = title.lower()
    has_negative = any(neg in t for neg in NON_ANGULAR_TITLE_INDICATORS)
    has_override = any(pos in t for pos in ANGULAR_TITLE_OVERRIDES)
    if has_negative and not has_override:
        return False
    return True

async def check_greenhouse(token: str) -> dict:
    """Check Greenhouse board for Angular mentions."""
    for base in ["boards-api.greenhouse.io", "boards-api.eu.greenhouse.io"]:
        url = f"https://{base}/v1/boards/{token}/jobs?content=true"
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get(url, headers={"Accept": "application/json"})
                if r.status_code == 200:
                    jobs = r.json().get("jobs", [])
                    angular_jobs = [
                        j for j in jobs
                        if "angular" in (j.get("title","") + " " + j.get("content","")).lower()
                        and is_likely_angular_role(j.get("title", ""))
                    ]
                    return {"total": len(jobs), "angular": len(angular_jobs), "status": "ok", "titles": [j["title"] for j in angular_jobs[:5]]}
        except: pass
    return {"total": 0, "angular": 0, "status": "api_404"}

async def check_lever(token: str) -> dict:
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(url, headers={"Accept": "application/json"})
            if r.status_code == 200:
                jobs = r.json()
                angular_jobs = [
                    j for j in jobs
                    if "angular" in (j.get("text","") + " " + j.get("descriptionPlain","")).lower()
                    and is_likely_angular_role(j.get("text", ""))
                ]
                return {"total": len(jobs), "angular": len(angular_jobs), "status": "ok", "titles": [j["text"] for j in angular_jobs[:5]]}
    except: pass
    return {"total": 0, "angular": 0, "status": "api_error"}

async def check_smartrecruiters(company_id: str) -> dict:
    url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings?q=Angular"
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(url, headers={"Accept": "application/json"})
            if r.status_code == 200:
                data = r.json()
                jobs = data.get("content", [])
                angular_jobs = [
                    j for j in jobs
                    if is_likely_angular_role(j.get("name", ""))
                ]
                return {"total": len(jobs), "angular": len(angular_jobs), "status": "ok", "titles": [j.get("name","") for j in angular_jobs[:5]]}
    except: pass
    return {"total": 0, "angular": 0, "status": "api_error"}

async def check_workday(url: str) -> dict:
    """Check Workday board for Angular mentions via the cxs API."""
    m = re.match(r"https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/(?:([^/]+)/)?([^/?]+)", url)
    if not m:
        return {"total": 0, "angular": 0, "status": "url_parse_error"}
    tenant, wd, lang, site = m.groups()
    host = f"{tenant}.{wd}.myworkdayjobs.com"
    api = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            # First: search for Angular specifically
            body = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": "Angular"}
            r = await c.post(api, json=body, headers=headers)
            if r.status_code != 200:
                return {"total": 0, "angular": 0, "status": f"api_{r.status_code}"}
            data = r.json()
            angular_jobs = data.get("jobPostings", [])
            
            # Filter titles using is_likely_angular_role
            angular_jobs_filtered = [
                j for j in angular_jobs
                if is_likely_angular_role(j.get("title", ""))
            ]
            
            # Also get overall count (no search filter)
            body_all = {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}
            r_all = await c.post(api, json=body_all, headers=headers)
            total_all = r_all.json().get("total", 0) if r_all.status_code == 200 else 0
            return {
                "total": total_all,
                "angular": len(angular_jobs_filtered),
                "status": "ok",
                "titles": [j.get("title", "") for j in angular_jobs_filtered[:5]]
            }
    except Exception as e:
        return {"total": 0, "angular": 0, "status": f"error: {str(e)[:50]}"}

async def check_phenom(url: str) -> dict:
    """Check Phenom portal for Angular mentions via API."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    api_paths = ["/api/apply/v2/jobs", "/api/jobs"]
    for path in api_paths:
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
                params = {"q": "Angular", "location": "India", "limit": "50"}
                r = await c.get(f"{base}{path}", params=params,
                                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                if r.status_code != 200:
                    continue
                data = r.json()
                jobs = data.get("jobs", [])
                if jobs or isinstance(data, list):
                    if isinstance(data, list):
                        jobs = data
                    angular_jobs = [
                        j for j in jobs
                        if is_likely_angular_role(j.get("title", ""))
                    ]
                    return {
                        "total": len(jobs),
                        "angular": len(angular_jobs),  # search was already filtered
                        "status": "ok",
                        "titles": [j.get("title", "") for j in angular_jobs[:5]]
                    }
        except:
            continue
    return {"total": 0, "angular": 0, "status": "phenom_api_unavailable"}

async def audit_company(company: dict) -> dict:
    url = company["url"].lower()
    name = company["name"]
    portal = company.get("portal_type", "generic")
    token = url.rstrip("/").split("/")[-1].split("?")[0]

    result = {"company": name, "portal_type": portal, "url": company["url"]}

    if portal == "greenhouse" or "greenhouse.io" in url:
        data = await check_greenhouse(token)
    elif portal == "lever" or "lever.co" in url:
        data = await check_lever(token)
    elif portal == "smartrecruiters" or "smartrecruiters.com" in url:
        data = await check_smartrecruiters(token)
    elif portal == "workday" or "myworkdayjobs.com" in url:
        data = await check_workday(company["url"])
    elif portal == "phenom":
        data = await check_phenom(company["url"])
    else:
        data = {"total": 0, "angular": 0, "status": "no_api_available"}

    result.update(data)
    if data["angular"] > 0:
        result["verdict"] = "CONFIRMED_ANGULAR"
    elif data["status"] in ("api_404", "api_error", "no_api_available", "phenom_api_unavailable"):
        result["verdict"] = "NEEDS_MANUAL_CHECK"
    else:
        result["verdict"] = "NO_ANGULAR"
    return result

async def main():
    all_companies = (
        [(c, "main") for c in main_companies] +
        [(c, "indian_product") for c in product_companies] +
        [(c, "service") for c in service_companies]
    )
    rows = []
    for company, cat in all_companies:
        result = await audit_company(company)
        result["category"] = cat
        rows.append(result)
        status_icon = "+" if result["verdict"] == "CONFIRMED_ANGULAR" else "-" if result["verdict"] == "NO_ANGULAR" else "?"
        print(f"  {status_icon} {result['company']:30s} | {result.get('total',0):3d} jobs | {result.get('angular',0):2d} angular | {result['verdict']}")

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["company","category","portal_type","url","total","angular","status","verdict","titles"])
        writer.writeheader()
        for r in rows:
            r["titles"] = json.dumps(r.get("titles", []))
            writer.writerow(r)
    print(f"\nReport saved to {OUTPUT}")
    confirmed = sum(1 for r in rows if r["verdict"] == "CONFIRMED_ANGULAR")
    no_angular = sum(1 for r in rows if r["verdict"] == "NO_ANGULAR")
    needs_check = sum(1 for r in rows if r["verdict"] == "NEEDS_MANUAL_CHECK")
    print(f"Results: {confirmed} confirmed Angular | {no_angular} no Angular | {needs_check} need manual check")

if __name__ == "__main__":
    asyncio.run(main())
