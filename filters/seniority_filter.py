import re
from typing import List
from utils.logger import get_logger

logger = get_logger("filter.seniority")

class SeniorityFilter:
    """Filters jobs based on seniority patterns in title or description."""
    
    @staticmethod
    def passes(text: str, patterns: List[str]) -> bool:
        """
        Returns True if the text matches ANY of the seniority regex patterns.
        If patterns list is empty, returns True.
        """
        if not patterns:
            return True
            
        text_lower = text.lower()
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
                
        return False
