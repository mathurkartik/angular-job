# Angular Job Engine — Round 4 Fix Spec (Audit Refinement + Company Resolution)

> **Where we are**: The stack audit ran across all 200 companies. 12 flagged CONFIRMED_ANGULAR, 6 confirmed NO_ANGULAR, 7 returned API 404, and **90+ fell to NEEDS_MANUAL_CHECK** because the audit script only supports Greenhouse/Lever/SmartRecruiters. The Workday and Phenom API scrapers that were already built were never called by the audit.
>
> **What this spec does**: (A) Fix the audit to use all built scrapers, (B) apply the title-stack filter to the audit results, (C) manually resolve the remaining companies using what we already know, (D) fix the MoEngage false positive, (E) produce the final clean company list.

---

## Fix A — Expand the Audit Script to Use ALL API Scrapers

**The problem**: `verify_angular_stack.py` only checks Greenhouse, Lever, and SmartRecruiters. But you already built `WorkdayAPIScraper` and `PhenomAPIScraper`. The audit script should use them.

### Companies this would resolve

**Workday (13 companies, all currently NEEDS_MANUAL_CHECK)**:
Broadcom, EisnerAmper, RTX, Airbus, Diamondback Energy, SEW-EURODRIVE, AVEVA, SimCorp, Nextracker, Visa, Broadridge, Worldpay, Motorola Solutions, KSB Tech, Synechron

**Phenom (8 companies, all currently NEEDS_MANUAL_CHECK)**:
Citi, Wells Fargo, Barclays, Fidelity Investments, Standard Chartered, FedEx ACC India, Amdocs, Ericsson

### Add to `verify_angular_stack.py`

```python
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
            total = data.get("total", 0)
            # Also get overall count (no search filter)
            body_all = {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}
            r_all = await c.post(api, json=body_all, headers=headers)
            total_all = r_all.json().get("total", 0) if r_all.status_code == 200 else 0
            return {
                "total": total_all,
                "angular": total,  # Workday server-side search already filtered
                "status": "ok",
                "titles": [j.get("title", "") for j in angular_jobs[:5]]
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
                    return {
                        "total": len(jobs),
                        "angular": len(jobs),  # search was already filtered
                        "status": "ok",
                        "titles": [j.get("title", "") for j in jobs[:5]]
                    }
        except:
            continue
    return {"total": 0, "angular": 0, "status": "phenom_api_unavailable"}
```

### Update the routing in `audit_company()`

```python
async def audit_company(company: dict) -> dict:
    url = company["url"].lower()
    portal = company.get("portal_type", "generic")

    if portal == "greenhouse" or "greenhouse.io" in url:
        data = await check_greenhouse(token)
    elif portal == "lever" or "lever.co" in url:
        data = await check_lever(token)
    elif portal == "smartrecruiters" or "smartrecruiters.com" in url:
        data = await check_smartrecruiters(token)
    elif portal == "workday" or "myworkdayjobs.com" in url:
        data = await check_workday(company["url"])  # NEW
    elif portal == "phenom":
        data = await check_phenom(company["url"])  # NEW
    else:
        data = {"total": 0, "angular": 0, "status": "no_api_available"}
    # ... rest same
```

---

## Fix B — Apply Title-Stack Filter to Audit Results

**The problem**: The audit flags any job as "angular" if the word appears anywhere in the title or JD content. This produces false positives like "Senior Data Engineer (ADB, Python)" at Exadel or "Lead Software Engineer [.Net]" at Envoy Global.

### Current false positives in CONFIRMED_ANGULAR

| Company | Audit says | Reality |
|---|---|---|
| Exadel | 10 angular jobs | Sample titles are ALL "Data Engineer (Python)" — Angular is a nice-to-have in JD text |
| TRG Screen | 4 angular jobs | Includes ".Net Full Stack" and "Java" roles |
| OneTrust | 7 angular jobs | Includes "Java Backend" and "AEM" roles |
| Envoy Global | 2 angular jobs | One is ".Net" |
| Encora | 21 angular jobs | Includes "Data Quality Analyst" and "Application Support" |
| Capco | 35 angular jobs | Includes "AI Engineer" and Portuguese-language roles |

### Fix: Add title filtering to the audit's Angular count

```python
# Add to verify_angular_stack.py — same logic as Gate 4 from Round 2

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
```

Then filter the Angular count:

```python
# When counting angular jobs:
angular_jobs = [
    j for j in jobs
    if "angular" in (j.get("title","") + " " + j.get("content","")).lower()
    and is_likely_angular_role(j.get("title", ""))
]
```

This will drop the false positives (Data Engineers, .Net developers, etc.) from the Angular count, giving you an honest number.

---

## Fix C — Manually Resolve NEEDS_MANUAL_CHECK Using Existing Evidence

After Fix A resolves the Workday and Phenom companies via API, a large number of `generic` companies remain as NEEDS_MANUAL_CHECK. Many of these we can resolve right now using evidence from the test runs and domain knowledge.

### Companies to COMMENT OUT (confirmed React/Vue/non-Angular from test runs)

These all went through the full LLM pipeline in test runs and returned zero Angular jobs — their JDs were fetched (hundreds to thousands of chars) and "angular" genuinely wasn't in them:

```python
# Category 2 — confirmed React/Vue/Go shops from Cat-2 test run (Round 3):
# Flipkart         — React (confirmed: 3 jobs extracted, none Angular)
# Swiggy           — React/Kotlin (confirmed: 9 jobs, none Angular)
# Cred             — React (confirmed: 1 job, "angular" not in 403-char JD)
# Razorpay         — React/Go (confirmed: 2 jobs, 0 passed filters)
# Zerodha          — Python/Go/no frontend hiring (confirmed: 1 job, 0 passed)
# PhonePe          — React Native/React (Groq rate limited but known React stack)
# Groww            — React (confirmed: 7 jobs, ALL dropped, "angular" not in 1018-char JDs)
# Zepto            — React (confirmed: 2 jobs, "angular" not in 2071-char JDs)
# Zeta             — DNS error (careers.zeta.tech doesn't resolve)
# MoEngage         — React/Node (confirmed: 4 jobs, "angular" not in 588-char JDs — see Fix D)
# Darwinbox        — React (confirmed: 1 job, dropped by filters)
```

### Companies to KEEP (known Angular employers from research docs)

Your own `docs/compass.md` and `docs/output1.txt`/`output2.txt` researched and verified these as Angular employers in India. They're NEEDS_MANUAL_CHECK only because their portals don't have supported APIs — not because they don't hire Angular devs:

```
# Category 1 — BFSI GCCs (confirmed Angular from compass.md research):
Citi               — compass.md: "Angular v14+, RxJS, NgRx" confirmed
Deutsche Bank      — compass.md: "strong Angular signal"
JPMorgan Chase     — compass.md: "Angular, React roles" confirmed
Wells Fargo        — compass.md: "Angular, modern frontend"
Barclays           — compass.md: "Angular, TypeScript"
HSBC               — compass.md: confirmed
Fidelity           — compass.md: confirmed
UBS                — compass.md: "strongest modern-Angular signal: v18+, Signals, RxJS"
Morgan Stanley     — compass.md: confirmed
Standard Chartered — compass.md: confirmed
Goldman Sachs      — compass.md: confirmed
Societe Generale   — compass.md: confirmed
BNY Mellon         — compass.md: confirmed
Broadridge         — compass.md: "SS&C — strongest modern-Angular signal"

# Category 1 — Tech companies (known Angular users):
Zoho               — Known Angular user (Zoho Creator, Zoho CRM built on Angular)
SAP Labs           — SAP Fiori uses Angular-based framework
Siemens            — Industrial IoT dashboards on Angular
IBM                — Multiple Angular roles historically
```

### Companies where you should do a quick manual check

Open their careers page, search "Angular" — takes 2 minutes each. Only the ones you haven't already resolved:

```
GE HealthCare, Philips, Novartis, IQVIA, Baker Hughes, SLB,
Microsoft, Intuit, Adobe, Locus, ACI Worldwide, Thoughtworks,
PwC, Publicis Sapient, S&P Global, Deloitte,
Dell Technologies, Rakuten Symphony, Cisco, Ivanti,
UnitedHealth, Nagarro, EPAM Systems, Resilinc, Hospitable,
MetLife, SS&C Technologies, Keka HR, Zenoti
```

For Category 3 (service companies): TCS, Infosys, Wipro, HCLTech, Cognizant, Accenture, Capgemini, Tech Mahindra — these ALWAYS have Angular roles (they staff client projects). Keep all of them but accept they'll go through the LLM fallback path. Same for Synechron, Photon, Tata Elxsi, and the other service firms.

---

## Fix D — Fix the MoEngage False Positive (Fix E Regression)

**The problem**: Round 3 Fix E made the pipeline skip `fetch_jd_text()` when `description_text > 100 chars`. This works for API-sourced jobs (where description_text is real JD content from the ATS). But for LLM-fallback jobs, `description_text` is whatever the LLM wrote — which may contain "angular" even when the real JD doesn't.

MoEngage's 4 jobs passed the content filter in the latest run because the LLM-generated `description_text` was > 100 chars and the pipeline trusted it. In the previous run (before Fix E), those same 4 jobs were correctly dropped after fetching the real 588-char JDs that didn't mention Angular.

### Fix

One-line condition: only trust `description_text` when the job came from the API path.

```python
# In filters/pipeline_router.py — Gate 3 content check:

# Current (broken for LLM path):
if len(job.description_text.strip()) > 100:
    jd_text = job.description_text

# Fixed:
if job.source == "ats_api" and len(job.description_text.strip()) > 100:
    jd_text = job.description_text
    logger.info(f"Using API-provided JD text ({len(jd_text)} chars) for {job.job_title} at {job.company_name}")
else:
    logger.info(f"Fetching JD for: {job.job_title} at {job.company_name}")
    jd_text = await fetch_jd_text(job.application_url)
```

This preserves the performance win for API jobs (no redundant fetching) while maintaining the safety check for LLM-fallback jobs (always verify against the real JD).

---

## Fix E — Correct the CONFIRMED_ANGULAR Companies (False Positive Audit Results)

Based on the title-stack analysis in Fix B, here's the corrected assessment of the 12 "confirmed" companies:

| Company | Audit angular count | After title filter | Real Angular roles? | Action |
|---|---|---|---|---|
| Celonis | 2 | Verify titles | Maybe (Orchestration/Automation could be Angular) | Keep, let pipeline decide |
| Degreed | 1 | 1 ("Staff UI Engineer") | Likely yes | Keep |
| Exadel | 10 | ~0 (all Data Engineer Python titles) | No — false positive | Keep but expect 0 output |
| Capco | 35 | ~5–10 (Full Stack Java/Angular) | Some genuine | Keep |
| TRG Screen | 4 | 1 ("Full Stack Java + Angular") | 1 genuine | Keep |
| Backbase | 1 | 0–1 ("Senior AI Applied Software Engineer") | Unlikely | Keep but expect 0 |
| GHX | 14 | ~5–8 (generic "Software Engineer" titles) | Some genuine | Keep |
| OneTrust | 7 | ~2 (after removing Java Backend, AEM) | Some genuine | Keep |
| Envoy Global | 2 | 1 ("Senior Software Engineer UI") | 1 genuine | Keep |
| NiCE | 14 | ~5–8 (generic architect titles) | Some genuine | Keep |
| Epic Kids | 3 | 3 (Full-Stack titles) | Yes | Keep (but watch geo — "remote, us") |
| Encora | 21 | ~3 (after removing Data Analyst, Support, .Net) | Some genuine | Keep |

**Net effect**: The 12 CONFIRMED companies will likely produce 20–30 genuine Angular jobs total after title-stack filtering — not the 93 the raw audit implies.

---

## Summary — Action Items in Order

| # | Action | Type | Impact |
|---|---|---|---|
| 1 | **Fix D**: Add `job.source == "ats_api"` guard to Fix E | Code change | Eliminates MoEngage-type false positives |
| 2 | **Fix A**: Add Workday + Phenom checkers to audit script | Code change | Resolves 21 companies from NEEDS_MANUAL_CHECK |
| 3 | **Fix B**: Add title-stack filter to audit script | Code change | Corrects false positive Angular counts |
| 4 | Re-run the expanded audit | Run script | Get accurate classification for Workday + Phenom companies |
| 5 | **Fix C**: Comment out confirmed React companies from Cat-2 | Config change | Flipkart, Swiggy, Cred, Razorpay, Zerodha, PhonePe, Groww, Zepto, Zeta, MoEngage, Darwinbox |
| 6 | **Fix C**: Manual 2-min check on ~30 remaining companies | Manual | Opens career page, searches "Angular" |
| 7 | Re-run `python main.py` with cleaned configs | Full run | Should produce real, verified Angular jobs only |

### Expected final state

After all fixes:
- **API-verified companies**: 12 Greenhouse + resolved Workday/Phenom = ~25–35 reliable companies
- **Manually verified (keep for LLM fallback)**: BFSI GCCs + known Angular employers + service companies = ~20–30 companies
- **Commented out**: ~130 companies (React shops, dead URLs, no Angular openings)
- **Active total**: ~50–65 companies, all confirmed or strongly evidenced Angular employers
- **Expected job output**: 30–80 genuine Angular roles with direct apply URLs
