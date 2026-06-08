import re
from typing import Dict, List, Tuple
from config.scoring_config import SCORING_PILLARS

def evaluate_pillars(text: str) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    """
    Evaluates the given text against the scoring pillars.
    Returns:
        - A dictionary of {pillar_name: raw_score (0.0 to 1.0)}
        - A dictionary of {pillar_name: [matched_keywords]}
    """
    text_lower = text.lower()
    
    scores = {}
    matched_keywords_dict = {}
    
    for pillar_name, config in SCORING_PILLARS.items():
        matched = []
        for kw in config["keywords"]:
            if re.search(rf'\b{re.escape(kw)}\b', text_lower):
                matched.append(kw)
                
        # Calculate score bounded to 1.0 max per pillar
        raw_score = len(matched) / config["full_marks_count"]
        scores[pillar_name] = min(raw_score, 1.0)
        matched_keywords_dict[pillar_name] = matched
        
    return scores, matched_keywords_dict
