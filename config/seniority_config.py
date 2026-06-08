"""
Seniority patterns per category.
"""

# Category 1: Strict — 8+ YOE, Senior/Lead titles
CATEGORY1_SENIORITY_PATTERNS = [
    r"senior", r"lead", r"staff", r"principal", r"architect",
    r"8\+?\s*(?:years|yrs|yoe)", r"7\+?\s*(?:years|yrs|yoe)",
    r"9\+?\s*(?:years|yrs|yoe)", r"1[0-9]\+?\s*(?:years|yrs|yoe)"
]

# Category 2: Relaxed — 5+ YOE accepted
CATEGORY2_SENIORITY_PATTERNS = [
    r"senior", r"lead", r"staff", r"principal", r"architect",
    r"[5-9]\+?\s*(?:years|yrs|yoe)", r"1[0-9]\+?\s*(?:years|yrs|yoe)"
]

# Category 3: No seniority filtering
