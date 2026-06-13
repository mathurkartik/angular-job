import json
import re
import time
from duckduckgo_search import DDGS

def get_new_url_and_portal(company_name):
    query = f"{company_name} careers software engineering jobs"
    try:
        results = DDGS().text(query, max_results=3)
        for r in results:
            url = r['href']
            # Avoid generic sites like linkedin, glassdoor, indeed
            if not any(domain in url.lower() for domain in ['linkedin.com', 'glassdoor.', 'indeed.', 'ambitionbox', 'naukri.com', 'foundit', 'wellfound']):
                
                # Determine portal
                portal = "generic"
                if "myworkdayjobs.com" in url or "workday.com" in url:
                    portal = "workday"
                elif "greenhouse.io" in url:
                    portal = "greenhouse"
                elif "lever.co" in url:
                    portal = "lever"
                
                return url, portal
    except Exception as e:
        print(f"Error searching for {company_name}: {e}")
    return None, None

def update_file(filepath, broken_list):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    updated = False
    for item in broken_list:
        name = item['name']
        new_url = item.get('new_url')
        new_portal = item.get('new_portal')
        if not new_url:
            continue
            
        # The regex targets the url and portal_type directly
        pattern = re.compile(r'(\{\s*"name"\s*:\s*"' + re.escape(name) + r'"\s*,\s*"url"\s*:\s*")[^"]*("\s*,\s*"portal_type"\s*:\s*")[^"]*("\s*,?)', re.DOTALL)
        
        def replacer(match):
            return match.group(1) + new_url + match.group(2) + new_portal + match.group(3)
            
        new_content, count = pattern.subn(replacer, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated {name} in {filepath}")
            
    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    with open('link_report.json', 'r') as f:
        broken_links = json.load(f)
        
    print(f"Fixing {len(broken_links)} broken links...")
    
    # Get new urls
    for i, item in enumerate(broken_links):
        name = item['name']
        print(f"[{i+1}/{len(broken_links)}] Searching for {name}...")
        url, portal = get_new_url_and_portal(name)
        if url:
            item['new_url'] = url
            item['new_portal'] = portal
            print(f"  Found: {url} ({portal})")
        else:
            print(f"  Not found.")
            
        time.sleep(1) # Be nice to DDG
        
    # Apply to files
    files = [
        'config/companies_main.py',
        'config/companies_indian_product.py',
        'config/companies_service.py'
    ]
    
    for filepath in files:
        update_file(filepath, broken_links)

if __name__ == "__main__":
    main()
