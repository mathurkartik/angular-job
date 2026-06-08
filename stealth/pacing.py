import asyncio
import random
from urllib.parse import urlparse
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("pacing")

class PacingManager:
    def __init__(self):
        self.domain_last_request = {}
        self.domain_failures = {}
        self.base_delay = 2.0
        self.max_delay = 120.0

    async def apply_delay(self, url: str):
        """Applies an exponential backoff delay based on domain failure history."""
        domain = urlparse(url).netloc
        
        # Calculate backoff based on previous failures
        failures = self.domain_failures.get(domain, 0)
        delay = min(self.base_delay * (2 ** failures), self.max_delay)
        
        # Add jitter (+/- 30%)
        jitter = random.uniform(-0.3, 0.3) * delay
        final_delay = delay + jitter

        # Ensure we respect the gap since the last request to this domain
        last_request = self.domain_last_request.get(domain)
        if last_request:
            elapsed = (datetime.now() - last_request).total_seconds()
            if elapsed < final_delay:
                wait_time = final_delay - elapsed
                logger.debug(f"Pacing: Waiting {wait_time:.2f}s before next request to {domain}")
                await asyncio.sleep(wait_time)

        self.domain_last_request[domain] = datetime.now()

    def record_failure(self, url: str):
        """Records a failure (e.g. 429 or captcha) to increase future delays."""
        domain = urlparse(url).netloc
        self.domain_failures[domain] = self.domain_failures.get(domain, 0) + 1
        logger.warning(f"Recorded failure for {domain}. Future delays will increase.")

    def record_success(self, url: str):
        """Resets the failure count for a domain upon success."""
        domain = urlparse(url).netloc
        if domain in self.domain_failures:
            del self.domain_failures[domain]

# Global instance for easy use
pacing_manager = PacingManager()
