import os
import re

files = [
    'config/companies_main.py',
    'config/companies_indian_product.py',
    'config/companies_service.py'
]

for filepath in files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Software with Engineer in URL parameters
    # This specifically looks for url assignments that contain Software
    new_content = re.sub(r'([?&](?:q|keywords|search|keyword))=Software', r'\1=Engineer', content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
    else:
        print(f"No changes for {filepath}")
