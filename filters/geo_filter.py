from typing import List
from utils.logger import get_logger

logger = get_logger("filter.geo")

class GeoFilter:
    """Filters jobs based on geographic whitelists."""
    
    @staticmethod
    def passes(location: str, whitelist: List[str]) -> bool:
        """
        Returns True if the normalized location matches any whitelist entry.
        If whitelist is empty, returns True (no geo filtering).
        """
        if not whitelist:
            return True
            
        loc = location.lower()
        
        for allowed in whitelist:
            if allowed in loc:
                return True
                
        return False
