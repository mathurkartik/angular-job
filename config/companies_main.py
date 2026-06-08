"""
Category 1: Main Companies (Primary Targets)
Foreign GCCs, Big Tech, Premium Consultancies, Remote Boards, Talent Networks.
"""

CATEGORY = "main"
CATEGORY_LABEL = "Category 1: Main Companies"

COMPANIES = [
    # --- Tier 1: Healthcare & Energy Domain Matches ---
    {"name": "GE HealthCare",  "tier": "Tier_1_Domain_Match",       "url": "https://careers.gehealthcare.com/global/en/", "portal_type": "generic"},
    {"name": "Philips",        "tier": "Tier_1_Domain_Match",       "url": "https://www.careers.philips.com/global/en/",  "portal_type": "generic"},
    {"name": "Novartis",       "tier": "Tier_1_Domain_Match",       "url": "https://www.novartis.com/careers/career-search/", "portal_type": "generic"},
    {"name": "IQVIA",          "tier": "Tier_1_Domain_Match",       "url": "https://jobs.iqvia.com/en/jobs/",            "portal_type": "generic"},
    {"name": "Baker Hughes",   "tier": "Tier_1_Domain_Match",       "url": "https://careers.bakerhughes.com/global/en/", "portal_type": "workday"},
    {"name": "SLB",            "tier": "Tier_1_Domain_Match",       "url": "https://apply.slb.com/careers/",             "portal_type": "generic"},

    # --- Tier 2: Big Tech & SaaS ---
    {"name": "Microsoft",      "tier": "Tier_2_Big_Tech",          "url": "https://careers.microsoft.com/v2/global/en/", "portal_type": "generic"},
    {"name": "Intuit",         "tier": "Tier_2_Big_Tech",          "url": "https://www.intuit.com/in/careers/",          "portal_type": "generic"},
    {"name": "SAP Labs",       "tier": "Tier_2_Big_Tech",          "url": "https://jobs.sap.com/go/India/8807201/",      "portal_type": "generic"},
    {"name": "Adobe",          "tier": "Tier_2_Big_Tech",          "url": "https://careers.adobe.com/us/en/",            "portal_type": "generic"},
    {"name": "Broadcom",       "tier": "Tier_2_Big_Tech",          "url": "https://careers.broadcom.com/",               "portal_type": "generic"},
    {"name": "Locus",          "tier": "Tier_2_Big_Tech",          "url": "https://locus.freshteam.com/jobs",            "portal_type": "generic"},
    {"name": "ACI Worldwide",  "tier": "Tier_2_Big_Tech",          "url": "https://ebwg.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/", "portal_type": "generic"},
    {"name": "EisnerAmper",    "tier": "Tier_2_Big_Tech",          "url": "https://eisneramper.wd1.myworkdayjobs.com/EisnerAmper_External/", "portal_type": "workday"},
    {"name": "Celonis",        "tier": "Tier_2_Big_Tech",          "url": "https://job-boards.greenhouse.io/celonis/",   "portal_type": "greenhouse"},
    {"name": "Creatio",        "tier": "Tier_2_Big_Tech",          "url": "https://jobs.eu.lever.co/creatio/",           "portal_type": "lever"},
    {"name": "RTX",            "tier": "Tier_2_Big_Tech",          "url": "https://globalhr.wd5.myworkdayjobs.com/en-US/REC_RTX_Ext_Gateway/", "portal_type": "workday"},
    {"name": "Airbus",         "tier": "Tier_2_Big_Tech",          "url": "https://ag.wd3.myworkdayjobs.com/en-US/Airbus/", "portal_type": "workday"},
    {"name": "Diamondback Energy", "tier": "Tier_2_Big_Tech",      "url": "https://diamondbackenergy.wd12.myworkdayjobs.com/DBE/", "portal_type": "workday"},
    {"name": "SEW-EURODRIVE",  "tier": "Tier_2_Big_Tech",          "url": "https://seweurodrive.wd5.myworkdayjobs.com/en-US/SEW/", "portal_type": "workday"},
    {"name": "AVEVA",          "tier": "Tier_2_Big_Tech",          "url": "https://aveva.wd3.myworkdayjobs.com/en-US/RIB_Careers/", "portal_type": "workday"},
    {"name": "SimCorp",        "tier": "Tier_2_Big_Tech",          "url": "https://simcorp.wd3.myworkdayjobs.com/en-US/SimCorp_Jobs/", "portal_type": "workday"},
    {"name": "Nextracker",     "tier": "Tier_2_Big_Tech",          "url": "https://nextracker.wd5.myworkdayjobs.com/en-US/nextpower_careers/", "portal_type": "workday"},

    # --- Tier 3: Premium Consultancies ---
    {"name": "Thoughtworks",   "tier": "Tier_3_Premium_Consulting", "url": "https://www.thoughtworks.com/careers/jobs/",  "portal_type": "greenhouse"},
    {"name": "Deloitte",       "tier": "Tier_3_Premium_Consulting", "url": "https://southasiacareers.deloitte.com/",      "portal_type": "generic"},
    {"name": "PwC",            "tier": "Tier_3_Premium_Consulting", "url": "https://jobs.pwc.com/",                       "portal_type": "generic"},
    {"name": "Publicis Sapient","tier": "Tier_3_Premium_Consulting","url": "https://careers.publicissapient.com/job-search","portal_type": "generic"},

    # --- Tier 4: FinTech & Product GCCs ---
    {"name": "JPMorgan Chase", "tier": "Tier_4_FinTech_GCC",       "url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/", "portal_type": "workday"},
    {"name": "Goldman Sachs",  "tier": "Tier_4_FinTech_GCC",       "url": "https://www.goldmansachs.com/careers/",       "portal_type": "generic"},
    {"name": "Visa",           "tier": "Tier_4_FinTech_GCC",       "url": "https://visa.wd5.myworkdayjobs.com/en-US/Visa/", "portal_type": "workday"},
    {"name": "S&P Global",     "tier": "Tier_4_FinTech_GCC",       "url": "https://careers.spglobal.com/jobs/",          "portal_type": "generic"},

    # --- Tier 5: Global Remote Boards ---
    {"name": "We Work Remotely","tier": "Tier_5_Global_Remote",    "url": "https://weworkremotely.com/remote-front-end-programming-jobs", "portal_type": "remote_board"},
    {"name": "Remote OK",      "tier": "Tier_5_Global_Remote",     "url": "https://remoteok.com/remote-angular-jobs",    "portal_type": "remote_board"},
    {"name": "Wellfound",      "tier": "Tier_5_Global_Remote",     "url": "https://wellfound.com/jobs",                  "portal_type": "remote_board"},

    # --- Tier 6: Global Talent Networks ---
    {"name": "Uplers",         "tier": "Tier_6_Talent_Network",    "url": "https://www.uplers.com/join-as-a-talent/",    "portal_type": "talent_network"},
    {"name": "Turing",         "tier": "Tier_6_Talent_Network",    "url": "https://www.turing.com/jobs",                 "portal_type": "talent_network"},
    {"name": "Toptal",         "tier": "Tier_6_Talent_Network",    "url": "https://www.toptal.com/careers",              "portal_type": "talent_network"},
    {"name": "Andela",         "tier": "Tier_6_Talent_Network",    "url": "https://andela.com/talent/",                  "portal_type": "talent_network"},
    {"name": "BairesDev",      "tier": "Tier_6_Talent_Network",    "url": "https://jobs.bairesdev.com/",                 "portal_type": "talent_network"},
    {"name": "Optimum",        "tier": "Tier_6_Talent_Network",    "url": "https://www.optimum.io/careers/",             "portal_type": "talent_network"},

    # --- New User-Provided Additions (Hubs & Remote) ---
    {"name": "Siemens",        "tier": "Tier_1_Domain_Match",      "url": "https://jobs.siemens.com/",                   "portal_type": "generic"},
    {"name": "Biofourmis",     "tier": "Tier_1_Domain_Match",      "url": "https://boards.greenhouse.io/biofourmis",     "portal_type": "greenhouse"},
    {"name": "UnitedHealth",   "tier": "Tier_1_Domain_Match",      "url": "https://careers.unitedhealthgroup.com/",      "portal_type": "generic"},
    {"name": "Degreed",        "tier": "Tier_2_Big_Tech",          "url": "https://boards.greenhouse.io/degreed",        "portal_type": "greenhouse"},
    {"name": "Ivanti",         "tier": "Tier_2_Big_Tech",          "url": "https://careers.ivanti.com/",                 "portal_type": "generic"},
    {"name": "Dell Technologies","tier":"Tier_2_Big_Tech",         "url": "https://jobs.dell.com/en",                    "portal_type": "generic"},
    {"name": "Rakuten Symphony","tier": "Tier_2_Big_Tech",         "url": "https://symphony.rakuten.com/careers",        "portal_type": "generic"},
    {"name": "Cisco",          "tier": "Tier_2_Big_Tech",          "url": "https://careers.cisco.com/",                  "portal_type": "generic"},
    {"name": "Extreme Networks","tier": "Tier_2_Big_Tech",         "url": "https://jobs.lever.co/extremenetworks",       "portal_type": "lever"},
    {"name": "Exadel",         "tier": "Tier_3_Premium_Consulting","url": "https://job-boards.greenhouse.io/exadelinc",  "portal_type": "greenhouse"},
    {"name": "Capco",          "tier": "Tier_3_Premium_Consulting","url": "https://boards.greenhouse.io/capco",          "portal_type": "greenhouse"},
    {"name": "Nagarro",        "tier": "Tier_3_Premium_Consulting","url": "https://www.builtin.com/companies/nagarro",   "portal_type": "generic"},
    {"name": "EPAM Systems",   "tier": "Tier_3_Premium_Consulting","url": "https://careers.epam.com/en/it-jobs/angular/india", "portal_type": "generic"},
    {"name": "TRG Screen",     "tier": "Tier_4_FinTech_GCC",       "url": "https://job-boards.eu.greenhouse.io/trgscreen","portal_type": "greenhouse"},
    {"name": "Backbase",       "tier": "Tier_4_FinTech_GCC",       "url": "https://job-boards.greenhouse.io/workatbackbase","portal_type": "greenhouse"},
    {"name": "Resilinc",       "tier": "Tier_5_Global_Remote",     "url": "https://himalayas.app/companies/resilinc/jobs","portal_type": "generic"},
    {"name": "Hospitable",     "tier": "Tier_5_Global_Remote",     "url": "https://jobgether.com/company/hospitable",    "portal_type": "generic"},
]
