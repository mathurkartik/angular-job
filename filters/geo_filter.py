from typing import List
from utils.logger import get_logger

logger = get_logger("filter.geo")

class GeoFilter:
    """Filters jobs based on geographic whitelists."""

    # Non-India location indicators — if ANY of these appear in the location string,
    # it's not an India job, even if "remote" also appears.
    NON_INDIA_MARKERS = [
        ", us", ", usa", "united states", "- usa", "- us",
        ", uk", ", united kingdom", "- uk",
        ", eu", "europe",
        ", sg", "singapore",
        ", ae", "dubai",
        "london", "new york", "san francisco", "seattle", "austin",
        "chicago", "boston", "denver", "toronto", "vancouver",
        "coventry", "gaydon",  # Tata Elxsi UK offices
    ]

    @staticmethod
    def passes(location: str, whitelist: List[str]) -> bool:
        """
        Returns True if the normalized location matches any whitelist entry.
        If whitelist is empty, returns True (no geo filtering).
        """
        if not whitelist:
            return True

        loc = location.lower().strip()

        # First: reject locations that are clearly outside India,
        # regardless of whether they contain a whitelisted substring
        if any(marker in loc for marker in GeoFilter.NON_INDIA_MARKERS):
            return False

        for allowed in whitelist:
            if allowed in loc:
                return True

        return False
