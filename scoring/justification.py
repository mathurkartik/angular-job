from typing import Dict, List

def generate_justification(matched_keywords: Dict[str, List[str]], total_score: float) -> str:
    """
    Generates a human-readable justification string based on what was matched.
    """
    if total_score == 0:
        return "No relevant keywords found."
        
    parts = []
    
    if matched_keywords.get("core_stack"):
        parts.append(f"Core Stack ({len(matched_keywords['core_stack'])} matches)")
        
    if matched_keywords.get("modern_angular"):
        parts.append("Modern Angular features detected")
        
    if matched_keywords.get("state_management"):
        state_tools = ", ".join(matched_keywords["state_management"])
        parts.append(f"State Management ({state_tools})")
        
    if matched_keywords.get("scale_enterprise"):
        parts.append("Enterprise Scale/Architecture focus")
        
    if not parts:
        return f"Partial match based on minor keywords."
        
    return "; ".join(parts) + "."
