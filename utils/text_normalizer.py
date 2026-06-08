import re
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """
    Strips HTML tags and normalizes whitespace from a raw HTML string.
    Returns plain text suitable for NLP/Regex processing.
    """
    if not html_content:
        return ""
        
    # Use BeautifulSoup to strip tags
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ")
    
    # Normalize whitespace (replace multiple spaces/newlines with a single space)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def normalize_location(location: str) -> str:
    """Normalizes location strings to lowercase for easier filtering."""
    if not location:
        return ""
    return location.strip().lower()
