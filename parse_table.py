import re

raw_table = """
| [SLB Careers](https://careers.slb.com/?utm_source=chatgpt.com) | Direct jobs portal ([SLB Careers][1]) |
| [Thoughtworks Careers](https://www.thoughtworks.com/careers?utm_source=chatgpt.com) | Global careers page ([Thoughtworks][2]) |
| [PwC Careers (India)](https://www.pwc.in/careers.html?utm_source=chatgpt.com) | India careers portal ([PwC][3]) |
| [JPMorgan Chase Careers](https://careers.jpmorgan.com/?utm_source=chatgpt.com) | |
| [Uplers Careers](https://www.uplers.com/careers/?utm_source=chatgpt.com) | |
| [Andela Careers](https://andela.com/careers/?utm_source=chatgpt.com) | |
| [Optimum Careers](https://www.optimum.com/careers?utm_source=chatgpt.com) | |
| [Ivanti Careers](https://www.ivanti.com/company/careers?utm_source=chatgpt.com) | |
| [SS&C Technologies Careers](https://www.ssctech.com/careers?utm_source=chatgpt.com) | |
| [Zoho Careers](https://www.zoho.com/careers/?utm_source=chatgpt.com) | |
| [Leadstream Careers](https://leadstream.com/careers/?utm_source=chatgpt.com) | |
| [Swiggy Careers](https://careers.swiggy.com/?utm_source=chatgpt.com) | |
| [Zepto Careers](https://www.zeptonow.com/careers?utm_source=chatgpt.com) | |
| [Zeta Careers](https://careers.zeta.tech/?utm_source=chatgpt.com) | |
| [Zenoti Careers](https://www.zenoti.com/careers?utm_source=chatgpt.com) | |
| [Icertis Careers](https://www.icertis.com/company/careers/?utm_source=chatgpt.com) | |
| [Druva Careers](https://www.druva.com/about/careers?utm_source=chatgpt.com) | |
| [Eightfold AI Careers](https://eightfold.ai/careers/?utm_source=chatgpt.com) | |
| [Edifecs Careers](https://www.edifecs.com/careers/?utm_source=chatgpt.com) | |
| [Amagi Careers](https://www.amagi.com/careers?utm_source=chatgpt.com) | |
| [Gupshup Careers](https://www.gupshup.io/company/careers?utm_source=chatgpt.com) | |
| [Capillary Technologies Careers](https://capillarytech.com/careers/?utm_source=chatgpt.com) | |
| [Kissflow Careers](https://kissflow.com/careers/?utm_source=chatgpt.com) | |
| [RateGain Careers](https://rategain.com/careers/?utm_source=chatgpt.com) | |
| [CleverTap Careers](https://clevertap.com/careers/?utm_source=chatgpt.com) | |
| [WebEngage Careers](https://webengage.com/careers/?utm_source=chatgpt.com) | |
| [Vymo Careers](https://vymo.com/careers/?utm_source=chatgpt.com) | |
| [ClearTax Careers](https://cleartax.in/careers?utm_source=chatgpt.com) | |
| [Khatabook Careers](https://khatabook.com/careers/?utm_source=chatgpt.com) | |
| [Navi Careers](https://navi.com/careers/?utm_source=chatgpt.com) | |
| [Lendingkart Careers](https://www.lendingkart.com/careers/?utm_source=chatgpt.com) | |
| [CoinDCX Careers](https://coindcx.com/careers/?utm_source=chatgpt.com) | |
| [CoinSwitch Careers](https://coinswitch.co/careers/?utm_source=chatgpt.com) | |
| [Mudrex Careers](https://mudrex.com/careers?utm_source=chatgpt.com) | |
| [Pratilipi Careers](https://careers.pratilipi.com/?utm_source=chatgpt.com) | |
| [Pocket FM Careers](https://pocketfm.com/careers?utm_source=chatgpt.com) | |
| [Kuku FM Careers](https://kukufm.com/careers/?utm_source=chatgpt.com) | |
| [Classplus Careers](https://classplusapp.com/careers/?utm_source=chatgpt.com) | |
| [Bizongo Careers](https://bizongo.com/careers/?utm_source=chatgpt.com) | |
| [ElasticRun Careers](https://elastic.run/careers/?utm_source=chatgpt.com) | |
| [Shiprocket Careers](https://www.shiprocket.in/careers/?utm_source=chatgpt.com) | |
| [Shadowfax Careers](https://www.shadowfax.in/careers/?utm_source=chatgpt.com) | |
| [Porter Careers](https://porter.in/careers?utm_source=chatgpt.com) | |
| [Log9 Materials Careers](https://log9materials.com/careers/?utm_source=chatgpt.com) | |
| [Euler Motors Careers](https://www.eulermotors.com/careers?utm_source=chatgpt.com) | |
| [SUN Mobility Careers](https://www.sunmobility.com/careers/?utm_source=chatgpt.com) | |
| [Simple Energy Careers](https://www.simpleenergy.in/careers?utm_source=chatgpt.com) | |
| [Chalo Careers](https://chalo.com/careers/?utm_source=chatgpt.com) | |
| [Zoomcar Careers](https://www.zoomcar.com/careers?utm_source=chatgpt.com) | |
| [Drivezy Careers](https://drivezy.com/careers?utm_source=chatgpt.com) | |
| [CarDekho Careers](https://careers.cardekho.com/?utm_source=chatgpt.com) | |
| [Spinny Careers](https://spinny.com/careers/?utm_source=chatgpt.com) | |
| [Cars24 Careers](https://www.cars24.com/careers/?utm_source=chatgpt.com) | |
| [Droom Careers](https://droom.in/careers?utm_source=chatgpt.com) | |
| [Square Yards Careers](https://www.squareyards.com/careers?utm_source=chatgpt.com) | |
| [NestAway Careers](https://www.nestaway.com/careers?utm_source=chatgpt.com) | |
| [PropTiger Careers](https://www.proptiger.com/careers?utm_source=chatgpt.com) | |
| [Zolo Careers](https://zolostays.com/careers?utm_source=chatgpt.com) | |
| [Stanza Living Careers](https://www.stanzaliving.com/careers?utm_source=chatgpt.com) | |
| [HomeLane Careers](https://www.homelane.com/careers?utm_source=chatgpt.com) | |
| [Design Cafe Careers](https://www.designcafe.com/careers/?utm_source=chatgpt.com) | |
| [Pepperfry Careers](https://www.pepperfry.com/careers.html?utm_source=chatgpt.com) | |
| [Furlenco Careers](https://www.furlenco.com/careers?utm_source=chatgpt.com) | |
| [Rentomojo Careers](https://www.rentomojo.com/careers?utm_source=chatgpt.com) | |
| [Wakefit Careers](https://www.wakefit.co/careers?utm_source=chatgpt.com) | |
| [The Sleep Company Careers](https://thesleepcompany.in/careers?utm_source=chatgpt.com) | |
| [Capgemini Careers](https://www.capgemini.com/careers/?utm_source=chatgpt.com) | |
| [Tech Mahindra Careers](https://careers.techmahindra.com/?utm_source=chatgpt.com) | |
| [Zensar Technologies Careers](https://www.zensar.com/careers/?utm_source=chatgpt.com) | |
| [Anblicks Careers](https://www.anblicks.com/careers/?utm_source=chatgpt.com) | |
| [eSparkBiz Careers](https://www.esparkinfo.com/career.html?utm_source=chatgpt.com) | |
"""

parsed_data = {}
for line in raw_table.strip().split('\n'):
    if not line.strip() or '---' in line:
        continue
    # Regex to match | [Company Name Careers](URL) | ... |
    match = re.search(r'\|\s*\[(.*?) Careers.*?\]\((.*?)\)\s*\|', line, re.IGNORECASE)
    if match:
        name = match.group(1).replace(" (India)", "").strip()
        url = match.group(2).replace("?utm_source=chatgpt.com", "").strip()
        
        # Some special cases for matching
        if name == "Zolo": name = "ZoloStay"
        if name == "Leadstream": name = "Leadstreams"
        
        parsed_data[name] = url

def update_file(filepath, parsed_data):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    updated = False
    for name, new_url in parsed_data.items():
        # Match "name": "Company", ... "url": "old_url"
        # We replace the url.
        pattern = re.compile(r'(\{\s*"name"\s*:\s*"' + re.escape(name) + r'"\s*,\s*"url"\s*:\s*")[^"]*("\s*,\s*"portal_type"\s*:\s*")[^"]*("\s*,?)', re.DOTALL)
        
        def replacer(match):
            return match.group(1) + new_url + match.group(2) + "generic" + match.group(3)
            
        new_content, count = pattern.subn(replacer, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated {name} to {new_url} in {filepath}")
            
    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

files = [
    'config/companies_main.py',
    'config/companies_indian_product.py',
    'config/companies_service.py'
]

for filepath in files:
    update_file(filepath, parsed_data)
    
print(f"Parsed {len(parsed_data)} companies.")
