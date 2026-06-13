"""
Category 1: Main Companies (Primary Targets)
Foreign GCCs, Big Tech, Premium Consultancies, Remote Boards, Talent Networks.
"""

CATEGORY = "main"
CATEGORY_LABEL = "Category 1: Main Companies"

COMPANIES = [
    # --- Tier 1: Global GCCs ---
    {"name": "GE HealthCare",  "tier": "Tier_1_Global_GCC",       "url": "https://careers.gehealthcare.com/global/en/search-results?keywords=Engineer", "portal_type": "generic"},
    {"name": "Philips",        "tier": "Tier_1_Global_GCC",       "url": "https://www.careers.philips.com/global/en/search-results?keywords=Engineer",  "portal_type": "generic"},
    {"name": "Novartis",       "tier": "Tier_1_Global_GCC",       "url": "https://www.novartis.com/careers/career-search?search_api_fulltext=Software", "portal_type": "generic"},
    {"name": "IQVIA",          "tier": "Tier_1_Global_GCC",       "url": "https://jobs.iqvia.com/en/jobs/?search=Engineer",            "portal_type": "generic"},
    {"name": "Baker Hughes",   "tier": "Tier_1_Global_GCC",       "url": "https://careers.bakerhughes.com/global/en/search-results?keywords=Engineer", "portal_type": "generic"},
    {"name": "SLB",            "tier": "Tier_1_Global_GCC",       "url": "https://careers.slb.com/job-search?query=Software",             "portal_type": "generic"},

    # --- Tier 2: Big Tech & SaaS ---
    {"name": "Microsoft",      "tier": "Tier_2_Big_Tech",          "url": "https://jobs.careers.microsoft.com/global/en/search?q=Engineer", "portal_type": "generic"},
    {"name": "Intuit",         "tier": "Tier_2_Big_Tech",          "url": "https://jobs.intuit.com/search-jobs?k=Software",          "portal_type": "generic"},
    {"name": "SAP Labs",       "tier": "Tier_2_Big_Tech",          "url": "https://jobs.sap.com/search/?q=Engineer",      "portal_type": "generic"},
    {"name": "Adobe",          "tier": "Tier_2_Big_Tech",          "url": "https://careers.adobe.com/us/en/search-results?keywords=Engineer",            "portal_type": "generic"},
    {"name": "Broadcom",       "tier": "Tier_2_Big_Tech",          "url": "https://broadcom.wd1.myworkdayjobs.com/External_Career?q=Engineer",               "portal_type": "workday"},
    {"name": "Locus",          "tier": "Tier_2_Big_Tech",          "url": "https://locus.freshteam.com/jobs",            "portal_type": "freshteam"},
    {"name": "ACI Worldwide",  "tier": "Tier_2_Big_Tech",          "url": "https://ebwg.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/requisitions?keyword=Engineer", "portal_type": "oracle"},
    {"name": "EisnerAmper",    "tier": "Tier_2_Big_Tech",          "url": "https://eisneramper.wd1.myworkdayjobs.com/EisnerAmper_External?q=Engineer", "portal_type": "workday"},
    {"name": "Celonis",        "tier": "Tier_2_Big_Tech",          "url": "https://job-boards.greenhouse.io/celonis/",   "portal_type": "greenhouse"},
    {"name": "Creatio",        "tier": "Tier_2_Big_Tech",          "url": "https://jobs.eu.lever.co/creatio/",           "portal_type": "lever"},
    {"name": "RTX",            "tier": "Tier_2_Big_Tech",          "url": "https://globalhr.wd5.myworkdayjobs.com/en-US/REC_RTX_Ext_Gateway?q=Engineer", "portal_type": "workday"},
    {"name": "Airbus",         "tier": "Tier_2_Big_Tech",          "url": "https://ag.wd3.myworkdayjobs.com/en-US/Airbus?q=Engineer", "portal_type": "workday"},
    {"name": "Diamondback Energy", "tier": "Tier_2_Big_Tech",      "url": "https://diamondbackenergy.wd12.myworkdayjobs.com/DBE?q=Engineer", "portal_type": "workday"},
    {"name": "SEW-EURODRIVE",  "tier": "Tier_2_Big_Tech",          "url": "https://seweurodrive.wd5.myworkdayjobs.com/en-US/SEW?q=Engineer", "portal_type": "workday"},
    {"name": "AVEVA",          "tier": "Tier_2_Big_Tech",          "url": "https://aveva.wd3.myworkdayjobs.com/en-US/RIB_Careers?q=Engineer", "portal_type": "workday"},
    {"name": "SimCorp",        "tier": "Tier_2_Big_Tech",          "url": "https://simcorp.wd3.myworkdayjobs.com/en-US/SimCorp_Jobs?q=Engineer", "portal_type": "workday"},
    {"name": "Nextracker",     "tier": "Tier_2_Big_Tech",          "url": "https://nextracker.wd5.myworkdayjobs.com/en-US/nextpower_careers?q=Engineer", "portal_type": "workday"},

    # --- Tier 3: Premium Consultancies ---
    {"name": "Thoughtworks",   "tier": "Tier_3_Premium_Consulting", "url": "https://www.thoughtworks.com/careers/jobs/",  "portal_type": "generic"},
    {"name": "Deloitte",       "tier": "Tier_3_Premium_Consulting", "url": "https://southasiacareers.deloitte.com/search/?q=Engineer",      "portal_type": "generic"},
    {"name": "PwC",            "tier": "Tier_3_Premium_Consulting", "url": "https://jobs.pwc.com/global/en/search-results?keywords=Engineer",                       "portal_type": "generic"},
    {"name": "Publicis Sapient","tier": "Tier_3_Premium_Consulting","url": "https://careers.publicissapient.com/job-search","portal_type": "generic"},

    # --- Tier 4: FinTech & Product GCCs ---
    {"name": "JPMorgan Chase", "tier": "Tier_4_FinTech_GCC",       "url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/", "portal_type": "oracle"},
    {"name": "Goldman Sachs",  "tier": "Tier_4_FinTech_GCC",       "url": "https://www.goldmansachs.com/careers/",       "portal_type": "generic"},
    {"name": "Visa",           "tier": "Tier_4_FinTech_GCC",       "url": "https://visa.wd5.myworkdayjobs.com/en-US/Visa/", "portal_type": "workday"},
    {"name": "S&P Global",     "tier": "Tier_4_FinTech_GCC",       "url": "https://careers.spglobal.com/jobs/",          "portal_type": "generic"},

    # --- Tier 5: Global Remote Boards ---
    {"name": "We Work Remotely","tier": "Tier_5_Global_Remote",    "url": "https://weworkremotely.com/remote-front-end-programming-jobs", "portal_type": "generic"},
    {"name": "Remote OK",      "tier": "Tier_5_Global_Remote",     "url": "https://remoteok.com/remote-angular-jobs",    "portal_type": "generic"},
    {"name": "Wellfound",      "tier": "Tier_5_Global_Remote",     "url": "https://wellfound.com/jobs",                  "portal_type": "generic"},

    # --- Tier 6: Global Talent Networks ---
    {"name": "Uplers",         "tier": "Tier_6_Talent_Network",    "url": "https://www.uplers.com/join-as-a-talent/",    "portal_type": "generic"},
    {"name": "Turing",         "tier": "Tier_6_Talent_Network",    "url": "https://www.turing.com/jobs",                 "portal_type": "generic"},
    {"name": "Toptal",         "tier": "Tier_6_Talent_Network",    "url": "https://www.toptal.com/careers",              "portal_type": "generic"},
    {"name": "Andela",         "tier": "Tier_6_Talent_Network",    "url": "https://andela.com/talent/",                  "portal_type": "generic"},
    {"name": "BairesDev",      "tier": "Tier_6_Talent_Network",    "url": "https://jobs.bairesdev.com/",                 "portal_type": "generic"},
    {"name": "Optimum",        "tier": "Tier_6_Talent_Network",    "url": "https://www.optimum.io/careers/",             "portal_type": "generic"},

    # --- New User-Provided Additions (Hubs & Remote) ---
    {"name": "Siemens",        "tier": "Tier_1_Global_GCC",      "url": "https://jobs.siemens.com/",                   "portal_type": "generic"},
    # Audited 2026-06-13: no Angular openings found
    # {"name": "Biofourmis",     "tier": "Tier_1_Global_GCC",      "url": "https://boards.greenhouse.io/biofourmis",     "portal_type": "greenhouse"},
    {"name": "UnitedHealth",   "tier": "Tier_1_Global_GCC",      "url": "https://careers.unitedhealthgroup.com/",      "portal_type": "generic"},
    {"name": "Degreed",        "tier": "Tier_2_Big_Tech",          "url": "https://boards.greenhouse.io/degreed",        "portal_type": "greenhouse"},
    {"name": "Ivanti",         "tier": "Tier_2_Big_Tech",          "url": "https://careers.ivanti.com/",                 "portal_type": "generic"},
    {"name": "Dell Technologies","tier":"Tier_2_Big_Tech",         "url": "https://jobs.dell.com/en",                    "portal_type": "generic"},
    {"name": "Rakuten Symphony","tier": "Tier_2_Big_Tech",         "url": "https://symphony.rakuten.com/careers",        "portal_type": "generic"},
    {"name": "Cisco",          "tier": "Tier_2_Big_Tech",          "url": "https://careers.cisco.com/",                  "portal_type": "generic"},
    # Audited 2026-06-13: no Angular openings found
    # {"name": "Extreme Networks","tier": "Tier_2_Big_Tech",         "url": "https://jobs.lever.co/extremenetworks",       "portal_type": "lever"},
    {"name": "Exadel",         "tier": "Tier_3_Premium_Consulting","url": "https://job-boards.greenhouse.io/exadelinc",  "portal_type": "greenhouse"},
    {"name": "Capco",          "tier": "Tier_3_Premium_Consulting","url": "https://boards.greenhouse.io/capco",          "portal_type": "greenhouse"},
    {"name": "Nagarro",        "tier": "Tier_3_Premium_Consulting","url": "https://www.builtin.com/companies/nagarro",   "portal_type": "generic"},
    {"name": "EPAM Systems",   "tier": "Tier_3_Premium_Consulting","url": "https://careers.epam.com/en/it-jobs/angular/india", "portal_type": "generic"},
    {"name": "TRG Screen",     "tier": "Tier_4_FinTech_GCC",       "url": "https://job-boards.eu.greenhouse.io/trgscreen","portal_type": "greenhouse"},
    {"name": "Backbase",       "tier": "Tier_4_FinTech_GCC",       "url": "https://job-boards.greenhouse.io/workatbackbase","portal_type": "greenhouse"},
    {"name": "Resilinc",       "tier": "Tier_5_Global_Remote",     "url": "https://himalayas.app/companies/resilinc/jobs","portal_type": "generic"},
    {"name": "Hospitable",     "tier": "Tier_5_Global_Remote",     "url": "https://jobgether.com/company/hospitable",    "portal_type": "generic"},
    {"name": "Citi", "tier": "Tier_1_Global_GCC", "url": "https://jobs.citi.com/search-jobs/Angular/India", "portal_type": "phenom"},
    {"name": "Deutsche Bank", "tier": "Tier_1_Global_GCC", "url": "https://careers.db.com/professionals/search-roles/?keyword=Angular&country=India", "portal_type": "generic"},
    {"name": "Morgan Stanley", "tier": "Tier_1_Global_GCC", "url": "https://www.morganstanley.com/careers/career-opportunities-search?keywords=Angular", "portal_type": "generic"},
    {"name": "BNY Mellon", "tier": "Tier_1_Global_GCC", "url": "https://bny.eightfold.ai/careers?query=Angular&location=India", "portal_type": "eightfold"},
    {"name": "UBS", "tier": "Tier_1_Global_GCC", "url": "https://jobs.ubs.com/search/?q=Angular&location=India", "portal_type": "generic"},
    {"name": "Societe Generale GSC", "tier": "Tier_1_Global_GCC", "url": "https://careers.societegenerale.com/en/search-jobs?keyword=Angular&location=India", "portal_type": "generic"},
    {"name": "Wells Fargo", "tier": "Tier_1_Global_GCC", "url": "https://www.wellsfargojobs.com/en/jobs/?search=Angular&location=India", "portal_type": "phenom"},
    {"name": "HSBC Technology India", "tier": "Tier_1_Global_GCC", "url": "https://mycareer.hsbc.com/en_GB/external/SearchJobs/?keyword=Angular&location=India", "portal_type": "generic"},
    {"name": "Barclays", "tier": "Tier_1_Global_GCC", "url": "https://search.jobs.barclays/search-jobs/Angular/India", "portal_type": "phenom"},
    {"name": "Fidelity Investments", "tier": "Tier_1_Global_GCC", "url": "https://jobs.fidelity.com/in/jobs/?search=Angular", "portal_type": "phenom"},
    {"name": "Broadridge", "tier": "Tier_1_Global_GCC", "url": "https://broadridge.wd5.myworkdayjobs.com/en-US/Careers?q=Angular", "portal_type": "workday"},
    {"name": "SS&C Technologies", "tier": "Tier_1_Global_GCC", "url": "https://wd1.myworkdaysite.com/en-US/recruiting/ssctech/SSCTechnologies?q=Angular", "portal_type": "generic"},
    {"name": "Standard Chartered", "tier": "Tier_1_Global_GCC", "url": "https://jobs.standardchartered.com/search-jobs?k=Angular&l=India", "portal_type": "phenom"},
    {"name": "MetLife", "tier": "Tier_1_Global_GCC", "url": "https://jobs.metlife.com/search-jobs/Angular/India", "portal_type": "generic"},
    {"name": "FedEx ACC India", "tier": "Tier_1_Global_GCC", "url": "https://careers.fedex.com/jobs?search=Angular&location=Hyderabad", "portal_type": "phenom"},
    {"name": "Amdocs", "tier": "Tier_2_Big_Tech", "url": "https://jobs.amdocs.com/careers?query=Angular&location=India", "portal_type": "phenom"},
    {"name": "Ericsson", "tier": "Tier_2_Big_Tech", "url": "https://jobs.ericsson.com/careers?query=Angular&location=india", "portal_type": "phenom"},
    {"name": "IBM", "tier": "Tier_2_Big_Tech", "url": "https://www.ibm.com/careers/search?q=Angular&field_keyword_05[0]=India", "portal_type": "generic"},
    {"name": "Zoho", "tier": "Tier_2_Big_Tech", "url": "https://careers.zoho.com/jobs/Careers?search=Angular", "portal_type": "generic"},
    {"name": "Worldpay", "tier": "Tier_1_Global_GCC", "url": "https://worldpay.wd5.myworkdayjobs.com/en-US/Worldpay_External_Careers_Site?q=Angular&location=India", "portal_type": "workday"},
    {"name": "Motorola Solutions", "tier": "Tier_2_Big_Tech", "url": "https://motorolasolutions.wd5.myworkdayjobs.com/en-US/Careers?q=Angular&location=India", "portal_type": "workday"},
    {"name": "KSB Tech", "tier": "Tier_1_Global_GCC", "url": "https://ksb.wd3.myworkdayjobs.com/en-US/KSB_ExternalCareerSite?q=Angular&location=India", "portal_type": "workday"},
    {"name": "Global Healthcare Exchange", "tier": "Tier_2_Big_Tech", "url": "https://boards.greenhouse.io/globalhealthcareexchangeinc?q=Angular&location=India", "portal_type": "greenhouse"},
    {"name": "OneTrust", "tier": "Tier_2_Big_Tech", "url": "https://boards.greenhouse.io/onetrust?q=Angular&location=India", "portal_type": "greenhouse"},
    {"name": "Envoy Global", "tier": "Tier_2_Big_Tech", "url": "https://boards.greenhouse.io/envoyglobalinc?q=Angular&location=India", "portal_type": "greenhouse"},
    {"name": "NiCE", "tier": "Tier_2_Big_Tech", "url": "https://boards.greenhouse.io/nice?q=Angular&location=India", "portal_type": "greenhouse"},
    {"name": "Epic Kids", "tier": "Tier_4_Global_Remote", "url": "https://boards.greenhouse.io/epickids?q=Angular&location=India", "portal_type": "greenhouse"},
    {"name": "Leadstreams", "tier": "Tier_4_Global_Remote", "url": "https://boards.greenhouse.io/leadstreams?q=Angular&location=India", "portal_type": "greenhouse"},
]
