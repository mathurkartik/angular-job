import re

class TitleFilter:
    """
    Ensures that the job is actually a Software Engineering / Frontend role.
    Drops unrelated roles (Sales, HR, Finance, etc.) that get pulled by generic portal scrapers.
    """
    
    # Core engineering keywords that indicate this is a tech role
    TECH_KEYWORDS = [
        "frontend", "front end", "front-end", "angular", "react", "ui", "ux", 
        "web", "full stack", "fullstack", "full-stack", "software", "engineer", 
        "developer", "programmer"
    ]
    
    # Aggressively drop roles that are Tech but NOT Frontend/Angular
    EXCLUDE_KEYWORDS = [
        "qa", "sdet", "test", "testing", "backend", "back end", "back-end", 
        "data", "machine learning", "ml", "ai", "artificial intelligence", 
        "devops", "sre", "cloud", "security", "network", "system", "systems", 
        "database", "infrastructure", "hardware", "firmware", "sales", "hr", 
        "finance", "support", "it", "administrator"
    ]
    
    @staticmethod
    def passes(title: str) -> bool:
        if not title:
            return False
            
        title_lower = title.lower()
        
        # First check if it contains any EXCLUDED keywords
        for keyword in TitleFilter.EXCLUDE_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', title_lower):
                return False

        # Then check if it contains any INCLUDED tech keywords
        for keyword in TitleFilter.TECH_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', title_lower):
                return True
                
        return False
