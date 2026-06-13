import httpx
import asyncio
import json
from config.companies_main import COMPANIES as c1
from config.companies_indian_product import COMPANIES as c2
from config.companies_service import COMPANIES as c3

all_c = c1 + c2 + c3

async def check(c):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = await client.get(c['url'], headers=headers)
            return c['name'], c['portal_type'], c['url'], r.status_code, str(r.url)
    except Exception as e:
        return c['name'], c['portal_type'], c['url'], str(e), ''

async def main():
    print(f"Checking {len(all_c)} companies...")
    results = []
    # Process in chunks of 20 to avoid overwhelming the network
    for i in range(0, len(all_c), 20):
        chunk = all_c[i:i+20]
        res = await asyncio.gather(*(check(c) for c in chunk))
        results.extend(res)
        print(f"Checked {len(results)}/{len(all_c)}")
        
    # Analyze the results
    wrong_links = []
    for name, portal, original_url, status, final_url in results:
        is_wrong = False
        reason = []
        
        # Check HTTP Status
        if isinstance(status, str): # Exception message
            is_wrong = True
            reason.append(f"Error: {status}")
        elif status >= 400 and status not in [403, 429]: # Ignore 403/429 as it could be bot protection
            is_wrong = True
            reason.append(f"HTTP {status}")
            
        # Check Portal Type Mismatch
        if portal == "workday" and "myworkdayjobs.com" not in str(final_url) and "myworkdayjobs.com" not in original_url:
            # Note: some workdays are behind custom domains, but usually redirect to myworkdayjobs
            is_wrong = True
            reason.append("Workday portal type but URL is not Workday")
            
        if portal == "greenhouse" and "greenhouse.io" not in str(final_url) and "greenhouse.io" not in original_url:
            is_wrong = True
            reason.append("Greenhouse portal type but URL is not Greenhouse")
            
        if portal == "lever" and "lever.co" not in str(final_url) and "lever.co" not in original_url:
            is_wrong = True
            reason.append("Lever portal type but URL is not Lever")

        # Generic portal but URL looks like Workday, Lever, Greenhouse
        if portal == "generic":
            if "myworkdayjobs.com" in str(final_url):
                is_wrong = True
                reason.append("Should be portal_type 'workday'")
            elif "greenhouse.io" in str(final_url):
                is_wrong = True
                reason.append("Should be portal_type 'greenhouse'")
            elif "lever.co" in str(final_url):
                is_wrong = True
                reason.append("Should be portal_type 'lever'")

        if is_wrong:
            wrong_links.append({
                "name": name,
                "portal": portal,
                "url": original_url,
                "final_url": final_url,
                "reason": " | ".join(reason)
            })

    with open('link_report.json', 'w') as f:
        json.dump(wrong_links, f, indent=4)
        
    print(f"Found {len(wrong_links)} potentially wrong links.")

if __name__ == "__main__":
    asyncio.run(main())
