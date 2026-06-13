"""
One-time ATS detection utility.
Run: python -m utils.detect_ats
Prints a summary of ATS classification and updates portal_type values.
"""
import re
from collections import Counter
from typing import List, Dict, Any, Tuple


def detect_ats(url: str) -> str:
    """Detect ATS platform from URL pattern."""
    u = url.lower()
    if "greenhouse.io" in u or "boards.greenhouse.io" in u or "job-boards.greenhouse.io" in u or "job-boards.eu.greenhouse.io" in u:
        return "greenhouse"
    if "lever.co" in u:
        return "lever"
    if "myworkdayjobs.com" in u or "/wday/" in u:
        return "workday"
    if "smartrecruiters.com" in u:
        return "smartrecruiters"
    if "ashbyhq.com" in u:
        return "ashby"
    if "oraclecloud.com" in u or "/hcmUI/" in u:
        return "oracle"
    if "phenom" in u or "/api/apply/" in u or "jobs.citi.com" in u or "search.jobs.barclays" in u or "jobs.fidelity.com" in u or "wellsfargojobs.com" in u or "jobs.standardchartered.com" in u or "careers.fedex.com" in u or "jobs.amdocs.com" in u or "jobs.ericsson.com" in u:
        return "phenom"
    if "icims.com" in u:
        return "icims"
    if "successfactors" in u or "sapsf" in u:
        return "successfactors"
    if "eightfold.ai" in u:
        return "eightfold"
    if "freshteam.com" in u:
        return "freshteam"
    return "generic"


def classify_companies(companies: List[Dict[str, Any]]) -> Tuple[Counter, Dict[str, List[str]]]:
    """Classify all companies and return summary stats + fallback details."""
    counts = Counter()
    fallback_details = {}  # ats_type -> [company names]
    
    for c in companies:
        detected = detect_ats(c["url"])
        counts[detected] += 1
        
        if detected in ("oracle", "icims", "successfactors", "eightfold", "freshteam", "generic"):
            if detected not in fallback_details:
                fallback_details[detected] = []
            fallback_details[detected].append(c["name"])
    
    return counts, fallback_details


def print_summary(all_companies: List[Dict[str, Any]], config_label: str = "All"):
    """Print ATS classification summary."""
    counts, fallback_details = classify_companies(all_companies)
    
    print(f"\n{'='*60}")
    print(f"ATS Classification Summary ({config_label})")
    print(f"{'='*60}")
    
    # API-supported ATS types
    api_types = ["greenhouse", "lever", "workday", "smartrecruiters", "ashby", "phenom"]
    api_total = 0
    for ats in api_types:
        count = counts.get(ats, 0)
        api_total += count
        if count > 0:
            print(f"  {ats:25s}: {count}")
    
    print(f"  {'-'*40}")
    print(f"  {'API-supported total':25s}: {api_total}")
    print()
    
    # Fallback types
    fallback_total = 0
    for ats, names in sorted(fallback_details.items()):
        count = len(names)
        fallback_total += count
        examples = ", ".join(names[:3])
        suffix = f" + {count - 3} more" if count > 3 else ""
        print(f"  {ats:25s}: {count} ({examples}{suffix}) -> fallback")
    
    print(f"  {'-'*40}")
    print(f"  {'Fallback total':25s}: {fallback_total}")
    print(f"\n  TOTAL: {api_total + fallback_total} companies")
    print(f"  API coverage: {api_total}/{api_total + fallback_total} ({100*api_total//(api_total + fallback_total) if (api_total + fallback_total) else 0}%)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    
    from config.companies_main import COMPANIES as MAIN
    from config.companies_indian_product import COMPANIES as PRODUCT
    from config.companies_service import COMPANIES as SERVICE
    
    all_companies = MAIN + PRODUCT + SERVICE
    
    # Print per-config summaries
    print_summary(MAIN, "Main Companies")
    print_summary(PRODUCT, "Indian Product")
    print_summary(SERVICE, "Service")
    print_summary(all_companies, "ALL COMPANIES")
    
    # Show what would change
    print("\nPortal type corrections needed:")
    print("-" * 60)
    changes = 0
    for c in all_companies:
        detected = detect_ats(c["url"])
        current = c.get("portal_type", "generic")
        if detected != current:
            print(f"  {c['name']:30s}: {current:20s} -> {detected}")
            changes += 1
    if changes == 0:
        print("  None — all portal_type values are correct.")
    else:
        print(f"\n  {changes} corrections needed.")
