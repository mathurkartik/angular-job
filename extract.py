import codecs
import re

with codecs.open('search_results.txt', 'r', 'utf-16le') as f:
    lines = f.readlines()

missing = []
current = ""
for l in lines:
    if 'Searching for' in l:
        match = re.search(r'Searching for (.*)\.\.\.', l)
        if match:
            current = match.group(1)
    elif 'Not found' in l:
        missing.append(current)

with open('C:\\Users\\KartikMathur\\.gemini\\antigravity-ide\\brain\\0e5cd0e5-048a-425d-bb9d-8eb869a5ab9d\\missing_companies_report.md', 'w', encoding='utf-8') as f:
    f.write('# Missing Companies\\n\\n')
    for m in missing:
        f.write(f'- {m}\\n')

print(f"Wrote {len(missing)} missing companies")
