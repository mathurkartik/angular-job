1. Middleman Talent Networks & Agencies (To Include)
These platforms connect global companies with remote Indian talent. They often act as the Employer of Record (EoR) or facilitate B2B contracting.

Uplers (Talent Network): https://www.uplers.com/join-as-a-talent/

Turing: https://www.turing.com/jobs

Toptal: https://www.toptal.com/careers

Andela: https://andela.com/talent/

BairesDev: https://jobs.bairesdev.com/

Optimum (Remote): https://www.optimum.io/careers/

2. Companies of Indian Origin: Domestic Unicorns (Separate Section)
These are high-growth Indian product companies. They offer great engineering cultures and scale, even though compensation structures differ from foreign GCCs.

Flipkart: https://www.flipkartcareers.com/

Swiggy: https://careers.swiggy.com/

Cred: https://careers.cred.club/

Razorpay: https://razorpay.com/jobs/

Zerodha: https://careers.zerodha.com/

PhonePe: https://www.phonepe.com/careers/

Groww: https://groww.in/careers

Zepto: https://www.zeptonow.com/careers

Paytm: https://jobs.lever.co/paytm

3. Traditional IT Service Firms (For Background Scraping)
These firms drive massive volume. Scraping them in the background gives you a pulse on which enterprise clients are outsourcing Angular migrations.

TCS (Tata Consultancy Services): https://www.tcs.com/careers/india

Infosys: https://www.infosys.com/careers/

Wipro: https://careers.wipro.com/

HCLTech: https://www.hcltech.com/careers

Cognizant: https://careers.cognizant.com/global/en

Accenture (India): https://www.accenture.com/in-en/careers

Capgemini (India): https://www.capgemini.com/in-en/careers/

Tech Mahindra: https://careers.techmahindra.com/

How to update your Python Engine for this:
You will want to add these to your config.py file with specific tier tags so your Exporter knows how to handle them.

Add this to your TARGET_COMPANIES array in config.py:

Python
    # --- Tier 6: Global Talent Networks ---
    {
        "name": "Uplers",
        "tier": "Tier_6_Talent_Network",
        "url": "https://www.uplers.com/join-as-a-talent/"
    },
    {
        "name": "Turing",
        "tier": "Tier_6_Talent_Network",
        "url": "https://www.turing.com/jobs"
    },
    # ... add the rest of the Talent Networks

    # --- Tier 7: Domestic Product & Unicorns ---
    {
        "name": "Swiggy",
        "tier": "Tier_7_Domestic_Unicorn",
        "url": "https://careers.swiggy.com/"
    },
    {
        "name": "Razorpay",
        "tier": "Tier_7_Domestic_Unicorn",
        "url": "https://razorpay.com/jobs/"
    },
    # ... add the rest of the Domestic Unicorns

    # --- Tier 8: Background Data (Service Firms) ---
    {
        "name": "Accenture",
        "tier": "Tier_8_Background_Service",
        "url": "https://www.accenture.com/in-en/careers"
    },
    {
        "name": "Cognizant",
        "tier": "Tier_8_Background_Service",
        "url": "https://careers.cognizant.com/global/en"
    },
    # ... add the rest of the Service Firms