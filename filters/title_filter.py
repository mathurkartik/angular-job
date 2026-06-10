import re

class TitleFilter:
    """
    Ensures that the job is actually a Software Engineering / Frontend role.
    Drops unrelated roles (Sales, HR, Finance, etc.) that get pulled by generic portal scrapers.
    """
    
    # Core engineering keywords that indicate this is a tech role
    TECH_KEYWORDS = [
        "engineer", "developer", "frontend", "front end", "front-end",
        "angular", "react", "ui", "ux", "software", "web", "programmer",
        "architect", "full stack", "fullstack", "full-stack", "backend",
        "back end", "back-end", "data", "ml", "devops", "qa", "sdet",
        "systems", "cloud", "technology", "tech lead", "sre"
    ]
    
    @staticmethod
    def passes(title: str) -> bool:
        if not title:
            return False
            
        title_lower = title.lower()
        
        # Check if any tech keyword is in the title
        for keyword in TitleFilter.TECH_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', title_lower):
                return True
                
        return False
