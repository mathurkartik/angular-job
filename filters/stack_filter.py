import re
from typing import List
from utils.logger import get_logger

logger = get_logger("filter.stack")

class StackFilter:
    """Filters jobs to ensure they are actually Angular jobs."""
    
    @staticmethod
    def passes(text: str) -> bool:
        """
        Returns True if the text contains explicit mention of Angular.
        Excludes false positives like 'AngularJS' if 'Angular 2+' or modern
        Angular isn't also mentioned (basic check).
        """
        text_lower = text.lower()
        
        # Must have 'angular'
        if "angular" not in text_lower:
            return False
            
        # If it only mentions angularjs and not just 'angular' (with space/boundary)
        # We can be stricter, but for now we just look for 'angular' as a word boundary
        if not re.search(r'\bangular\b', text_lower):
            # Might just be 'angularjs'
            if "angularjs" in text_lower and "angular 2" not in text_lower and "angular 1" not in text_lower:
                logger.debug("Rejected likely AngularJS-only role.")
                return False
                
        return True
