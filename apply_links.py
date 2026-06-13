import re
import os

with open('parse_table.py', 'r', encoding='utf-8') as f:
    # Just run the parsing part we already wrote
    pass

from parse_table import parsed_data

files = [
    'config/companies_main.py',
    'config/companies_indian_product.py',
    'config/companies_service.py'
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    updated = False
    in_company = None
    for i, line in enumerate(lines):
        # check if line has name
        match = re.search(r'"name"\s*:\s*"(.*?)"', line)
        if match:
            in_company = match.group(1)
        
        # if we are in a company and see url
        if in_company and '"url"' in line:
            if in_company in parsed_data:
                old_url_match = re.search(r'"url"\s*:\s*"(.*?)"', line)
                if old_url_match:
                    new_url = parsed_data[in_company]
                    lines[i] = line.replace(old_url_match.group(1), new_url)
                    updated = True
                    print(f"Updated URL for {in_company} to {new_url}")
        
        # if we see portal type
        if in_company and '"portal_type"' in line:
            if in_company in parsed_data:
                old_portal_match = re.search(r'"portal_type"\s*:\s*"(.*?)"', line)
                if old_portal_match:
                    lines[i] = line.replace(f'"{old_portal_match.group(1)}"', '"generic"')
                    print(f"Updated portal for {in_company} to generic")
                    in_company = None # Done with this company
            
    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
