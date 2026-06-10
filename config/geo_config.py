"""
Geographic whitelists per category. Category 3 has no geo filter.
"""

# Category 1: Strict — only target cities + remote
CATEGORY1_GEO_WHITELIST = [
    "bengaluru", "bangalore", "bengaluru/hyderabad",
    "hyderabad", "secunderabad",
    "remote", "work from home", "wfh", "global remote", "anywhere",
    "not specified", "unknown"
]
# NOTE: "india" is deliberately excluded — it would false-positive
# on Gurgaon, Pune, Chennai, Noida, etc.

# Category 2: Relaxed — any Indian city accepted
CATEGORY2_GEO_WHITELIST = [
    "bengaluru", "bangalore", "hyderabad", "secunderabad",
    "mumbai", "pune", "gurgaon", "gurugram", "noida", "delhi",
    "chennai", "kolkata", "ahmedabad", "jaipur", "kochi",
    "india", "remote", "work from home", "wfh",
    "not specified", "unknown"
]

# Category 3: No geographic filtering (capture everything)
