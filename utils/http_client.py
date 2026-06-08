"""
utils/http_client.py — Resilient, rate-limited async HTTP client.

This module wraps aiohttp with three layers of protection against bot detection:

1. **User-Agent Rotation**: Every request gets a fresh, realistic browser UA string
   via the fake-useragent library, so the server never sees the same fingerprint twice.

2. **Randomized Rate Limiting**: A random sleep (between MIN_DELAY and MAX_DELAY from
   config) is injected *before* each request. This breaks uniform timing patterns that
   WAFs flag as automated traffic.

3. **Exponential Backoff Retries**: Transient failures (429, 503, connection drops) are
   retried up to MAX_RETRIES times with tenacity's exponential backoff + jitter, giving
   the target server time to recover without hammering it.

Usage:
    async with HttpClient() as client:
        html = await client.fetch("https://example.com/careers")
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Optional

import aiohttp
from fake_useragent import UserAgent
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
    RetryError,
)

from config import MIN_DELAY, MAX_DELAY, MAX_RETRIES, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Custom exception for HTTP errors that should trigger a retry
# ──────────────────────────────────────────────────────────────────────────────

class RetryableHTTPError(Exception):
    """Raised on 429 / 503 responses so tenacity can catch and retry them."""

    def __init__(self, status: int, url: str) -> None:
        self.status = status
        self.url = url
        super().__init__(f"HTTP {status} from {url}")


class NonRetryableHTTPError(Exception):
    """Raised on 4xx (except 429) errors that should NOT be retried."""

    def __init__(self, status: int, url: str) -> None:
        self.status = status
        self.url = url
        super().__init__(f"HTTP {status} from {url}")


# ──────────────────────────────────────────────────────────────────────────────
# The main HTTP client class
# ──────────────────────────────────────────────────────────────────────────────

class HttpClient:
    """
    Async HTTP client with built-in anti-bot protections.

    Designed as an async context manager so the underlying aiohttp session
    is properly created and torn down:

        async with HttpClient() as client:
            html = await client.fetch(url)
    """

    def __init__(
        self,
        min_delay: float = MIN_DELAY,
        max_delay: float = MAX_DELAY,
        max_retries: int = MAX_RETRIES,
        timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        self._min_delay = min_delay
        self._max_delay = max_delay
        self._max_retries = max_retries
        self._timeout = timeout

        # Initialize the User-Agent rotator.  fallback= ensures we always
        # get a valid string even if the UA database fetch fails.
        self._ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/125.0.0.0 Safari/537.36")

        self._session: Optional[aiohttp.ClientSession] = None
        self._request_count: int = 0  # lifetime counter for diagnostics

    # ── Context manager protocol ─────────────────────────────────────────

    async def __aenter__(self) -> "HttpClient":
        """Create the aiohttp session with sensible defaults."""
        timeout_cfg = aiohttp.ClientTimeout(total=self._timeout)
        self._session = aiohttp.ClientSession(
            timeout=timeout_cfg,
            # Accept compressed responses to save bandwidth
            headers={"Accept-Encoding": "gzip, deflate, br"},
            # Don't raise on non-2xx — we handle status codes ourselves
            raise_for_status=False,
            # Follow redirects (career pages love 301/302 chains)
            cookie_jar=aiohttp.CookieJar(unsafe=True),
        )
        logger.info("HttpClient session opened.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Ensure the session is closed cleanly, even on errors."""
        if self._session and not self._session.closed:
            await self._session.close()
            # Give the SSL transport a moment to shut down gracefully
            # (avoids "Unclosed connector" ResourceWarnings)
            await asyncio.sleep(0.25)
            logger.info(
                "HttpClient session closed after %d requests.", self._request_count
            )

    # ── Public API ───────────────────────────────────────────────────────

    async def fetch(self, url: str, extra_headers: Optional[dict] = None) -> str:
        """
        Fetch a URL and return its body as text (usually HTML).

        The call is wrapped with:
          • a random pre-request delay  (anti-pattern-detection)
          • a rotated User-Agent header  (anti-fingerprinting)
          • tenacity retries on 429/503  (resilience)

        Args:
            url:           The page to fetch.
            extra_headers: Any additional headers to merge in (e.g. Referer).

        Returns:
            The response body decoded as UTF-8 text.

        Raises:
            NonRetryableHTTPError: On 4xx errors (other than 429).
            RetryError:            If all retries are exhausted on 429/503.
            aiohttp.ClientError:   On network-level failures after retries.
        """
        return await self._fetch_with_retry(url, extra_headers)

    # ── Internal retry-wrapped fetcher ───────────────────────────────────

    @retry(
        # Retry only on errors we know are transient
        retry=retry_if_exception_type((RetryableHTTPError, aiohttp.ClientError)),
        # Exponential backoff: 1s → 2s → 4s … capped at 30s, plus random jitter
        wait=wait_exponential_jitter(initial=1, max=30, jitter=2),
        # Number of attempts (not retries — first try + N-1 retries)
        stop=stop_after_attempt(MAX_RETRIES + 1),
        # Log each retry so we can see what's happening
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _fetch_with_retry(
        self, url: str, extra_headers: Optional[dict] = None
    ) -> str:
        """
        Inner fetch method decorated with tenacity retry logic.

        The @retry decorator intercepts RetryableHTTPError (429/503) and
        aiohttp.ClientError (connection reset, DNS failure, etc.) and
        re-invokes this method after an exponentially increasing delay.
        """
        if self._session is None or self._session.closed:
            raise RuntimeError(
                "HttpClient must be used as an async context manager. "
                "Wrap usage in: async with HttpClient() as client: ..."
            )

        # ── Step 1: Random delay before the request ──────────────────────
        # This is the single most important anti-bot measure.  Uniform
        # inter-request timing is the easiest signal for a WAF to detect.
        delay = random.uniform(self._min_delay, self._max_delay)
        logger.debug("Sleeping %.2fs before requesting %s", delay, url)
        await asyncio.sleep(delay)

        # ── Step 2: Build headers with a fresh User-Agent ────────────────
        headers = {
            "User-Agent": self._ua.random,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            # Pretend we came from Google — many career sites serve richer
            # content to visitors who arrive via search engines
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        if extra_headers:
            headers.update(extra_headers)

        # ── Step 3: Make the request ─────────────────────────────────────
        self._request_count += 1
        logger.info(
            "[Request #%d] GET %s  (UA: %s…)",
            self._request_count,
            url,
            headers["User-Agent"][:50],
        )

        async with self._session.get(url, headers=headers, allow_redirects=True) as resp:
            status = resp.status

            # ── Step 4: Handle response status ───────────────────────────
            if status in (429, 503):
                # These are transient — the server is rate-limiting us or
                # temporarily down.  Raise so tenacity retries after backoff.
                logger.warning(
                    "Got HTTP %d from %s — will retry with backoff.", status, url
                )
                raise RetryableHTTPError(status, url)

            if 400 <= status < 500:
                # Client errors (403 Forbidden, 404 Not Found, etc.) are
                # unlikely to resolve on retry, so fail immediately.
                logger.error("HTTP %d (non-retryable) from %s", status, url)
                raise NonRetryableHTTPError(status, url)

            if status >= 500:
                # Other server errors (500, 502, 504) — treat as transient.
                logger.warning(
                    "Got HTTP %d from %s — will retry with backoff.", status, url
                )
                raise RetryableHTTPError(status, url)

            # ── Step 5: Read and return the body ─────────────────────────
            body = await resp.text(encoding="utf-8", errors="replace")
            logger.debug(
                "Received %d bytes from %s (HTTP %d)",
                len(body),
                url,
                status,
            )
            return body

    # ── Diagnostics ──────────────────────────────────────────────────────

    @property
    def request_count(self) -> int:
        """Total number of HTTP requests made in this session."""
        return self._request_count
