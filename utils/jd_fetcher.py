import httpx
from bs4 import BeautifulSoup
from utils.logger import get_logger

logger = get_logger("jd_fetcher")

async def fetch_jd_text(url: str) -> str:
    """
    Fetches the raw text from a job description URL.
    Returns the lowercased text for easy keyword matching.
    """
    try:
        # Use a timeout of 15 seconds to avoid hanging on bad pages
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            response = await client.get(str(url), headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Extract text, removing script/style tags
                for element in soup(["script", "style"]):
                    element.extract()
                text = soup.get_text(separator=" ", strip=True)
                return text.lower()
            else:
                logger.warning(f"Failed to fetch JD {url}: HTTP {response.status_code}")
    except Exception as e:
        logger.warning(f"Error fetching JD {url}: {str(e)}")
        
    return ""
