"""
scrapers/career_page_scraper.py — Playwright-powered career page scraper.

This scraper handles the hard case: career pages that render job listings
entirely in JavaScript (React/Vue/Angular SPAs, Workday iframes, etc.).
A simple HTTP GET would return an empty shell — we need a real browser.

Architecture:
  1. Launch headless Chromium via Playwright
  2. Navigate to the company's career page
  3. Wait for JS rendering to complete (network idle)
  4. Extract the rendered HTML and hand it to BeautifulSoup for parsing
  5. Identify job links whose titles match our TARGET_TITLES keywords
  6. Visit each matching job's detail page to extract the full description
  7. Return structured JobListing objects

Anti-bot measures inherited from the pipeline:
  • Randomized delays between page navigations (via asyncio.sleep)
  • Realistic viewport, locale, and timezone settings
  • Disabled webdriver flag to avoid navigator.webdriver detection
  • All browser contexts and pages are closed in finally blocks

Platform-specific parsers:
  The scraper includes specialised extraction logic for common ATS
  platforms (Lever, Greenhouse, Workday) with a generic fallback for
  custom career pages.
"""

from __future__ import annotations

import asyncio
import random
import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from config import (
    MIN_DELAY,
    MAX_DELAY,
    PAGE_LOAD_TIMEOUT,
    TARGET_TITLES,
    TARGET_LOCATIONS,
)
from schemas.job_listing import JobListing
from scrapers.base_scraper import BaseScraper


# ──────────────────────────────────────────────────────────────────────────────
# Compiled regex patterns (built once, reused across all scrapes)
# ──────────────────────────────────────────────────────────────────────────────

# Matches any of our target job title keywords in link text.
# Example: "Senior Angular Developer" matches because it contains "angular".
_TITLE_PATTERN = re.compile(
    "|".join(re.escape(kw) for kw in TARGET_TITLES),
    re.IGNORECASE,
)

# Matches our target cities in location strings.
_LOCATION_PATTERN = re.compile(
    "|".join(re.escape(loc) for loc in TARGET_LOCATIONS),
    re.IGNORECASE,
)


class CareerPageScraper(BaseScraper):
    """
    Scrapes company career pages using a headless Chromium browser.

    This class manages the full Playwright lifecycle (browser launch → context
    creation → page navigation → teardown) and delegates HTML parsing to
    platform-specific or generic extraction methods.

    Usage::

        scraper = CareerPageScraper()
        company = {"name": "Visa", "tier": "Tier_4_FinTech_GCC", "url": "https://..."}
        listings = await scraper.scrape(company)
    """

    def __init__(self, headless: bool = True) -> None:
        super().__init__()
        self._headless = headless

        # Playwright lifecycle objects — initialised in _do_scrape
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    # ── Core scrape implementation ───────────────────────────────────────

    async def _do_scrape(
        self, company_name: str, tier: str, target_url: str
    ) -> list[JobListing]:
        """
        Orchestrate the Playwright scraping flow for a single company.

        Steps:
          1. Launch browser if not already running
          2. Detect the ATS platform (Lever, Greenhouse, Workday, generic)
          3. Call the appropriate extractor
          4. Close browser resources in the finally block
        """
        listings: list[JobListing] = []

        try:
            # ── Launch Playwright and Chromium ───────────────────────────
            self._playwright = await async_playwright().start()

            self._browser = await self._playwright.chromium.launch(
                headless=self._headless,
                # These args reduce the browser's fingerprint and resource usage
                args=[
                    "--disable-blink-features=AutomationControlled",  # hide webdriver
                    "--disable-extensions",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",  # avoid /dev/shm issues in containers
                ],
            )

            self._logger.info("Chromium launched (headless=%s)", self._headless)

            # ── Detect ATS platform and dispatch ─────────────────────────
            platform = self._detect_platform(target_url)
            self._logger.info(
                "Detected platform: [bold magenta]%s[/] for %s",
                platform,
                company_name,
            )

            if platform == "lever":
                listings = await self._scrape_lever(company_name, tier, target_url)
            elif platform == "greenhouse":
                listings = await self._scrape_greenhouse(company_name, tier, target_url)
            elif platform == "workday":
                listings = await self._scrape_workday(company_name, tier, target_url)
            else:
                listings = await self._scrape_generic(company_name, tier, target_url)

        finally:
            # ── Cleanup: always close browser resources ──────────────────
            # This runs even if an exception occurred above, preventing
            # orphaned Chromium processes from leaking memory.
            await self._cleanup()

        return listings

    # ── Platform detection ───────────────────────────────────────────────

    @staticmethod
    def _detect_platform(url: str) -> str:
        """
        Identify the Applicant Tracking System from the URL pattern.

        Most companies use one of three major ATS platforms, each with
        a recognisable URL structure.  Knowing the platform lets us use
        targeted CSS selectors instead of guessing.
        """
        url_lower = url.lower()
        if "lever.co" in url_lower or "jobs.lever.co" in url_lower:
            return "lever"
        if "greenhouse.io" in url_lower or "boards.greenhouse.io" in url_lower:
            return "greenhouse"
        if "myworkdayjobs.com" in url_lower or "workday.com" in url_lower:
            return "workday"
        return "generic"

    # ── Browser context factory ──────────────────────────────────────────

    async def _create_context(self) -> BrowserContext:
        """
        Create a browser context with realistic fingerprinting.

        Each context is isolated (separate cookies, storage) so that
        one company's site can't see cookies from another.  The viewport,
        locale, and timezone are set to mimic a real Indian user on a
        1080p monitor.
        """
        context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            # Block images, fonts, and media to speed up page loads
            # (we only need the text content)
            extra_http_headers={
                "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
            },
        )

        # Suppress navigator.webdriver — many bot detectors check this flag.
        # By injecting this script before any page script runs, we ensure
        # the property always returns undefined/false.
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        return context

    # ── Shared page-loading helper ───────────────────────────────────────

    async def _navigate_and_wait(self, page: Page, url: str) -> str:
        """
        Navigate to *url*, wait for the page to stabilise, and return HTML.

        We try "networkidle" first (no network activity for 500ms), which
        works well for most SPAs.  If that times out (some pages keep
        long-polling), we fall back to "domcontentloaded" which is faster
        but may miss late-loading content.

        Returns:
            The fully-rendered HTML of the page.
        """
        try:
            await page.goto(url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT)
        except PlaywrightTimeoutError:
            self._logger.warning(
                "networkidle timed out for %s — falling back to domcontentloaded", url
            )
            try:
                await page.goto(
                    url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT
                )
                # Give JS a few extra seconds to render after DOM is ready
                await page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                self._logger.warning(
                    "domcontentloaded also timed out for %s — using partial content", url
                )

        return await page.content()

    # ── Anti-bot delay helper ────────────────────────────────────────────

    @staticmethod
    async def _random_delay() -> None:
        """
        Sleep a random duration between MIN_DELAY and MAX_DELAY.

        Called between page navigations to simulate human browsing speed.
        """
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        await asyncio.sleep(delay)

    # ══════════════════════════════════════════════════════════════════════
    # LEVER — jobs.lever.co/<company>
    # ══════════════════════════════════════════════════════════════════════
    # Lever renders a clean list of postings grouped by department.
    # Each posting is a clickable <a> with class "posting-title".

    async def _scrape_lever(
        self, company_name: str, tier: str, target_url: str
    ) -> list[JobListing]:
        """Extract job listings from a Lever career page."""
        context = await self._create_context()
        listings: list[JobListing] = []

        try:
            page = await context.new_page()
            html = await self._navigate_and_wait(page, target_url)
            soup = BeautifulSoup(html, "lxml")

            # Lever structure:
            #   <div class="posting">
            #     <a class="posting-title" href="/company/job-id">
            #       <h5>Job Title</h5>
            #     </a>
            #     <div class="posting-categories">
            #       <span class="sort-by-location posting-category">Location</span>
            #     </div>
            #   </div>
            postings = soup.select("div.posting")
            self._logger.info("Lever: found %d total postings", len(postings))

            for posting in postings:
                title_tag = posting.select_one("a.posting-title h5, a.posting-title")
                if not title_tag:
                    continue

                title_text = title_tag.get_text(strip=True)

                # ── Filter: does the title match our target keywords? ────
                if not _TITLE_PATTERN.search(title_text):
                    continue

                # ── Extract location ─────────────────────────────────────
                location_tag = posting.select_one(
                    "span.sort-by-location, span.posting-category"
                )
                location = location_tag.get_text(strip=True) if location_tag else ""

                # ── Filter: is it in our target cities? ──────────────────
                if not _LOCATION_PATTERN.search(location):
                    continue

                # ── Extract the job URL ──────────────────────────────────
                link_tag = posting.select_one("a.posting-title")
                if not link_tag or not link_tag.get("href"):
                    continue
                job_url = self.make_absolute_url(target_url, link_tag["href"])

                # ── Fetch the full job description from the detail page ──
                await self._random_delay()
                description = await self._fetch_job_description(
                    context, job_url, platform="lever"
                )

                listings.append(
                    JobListing(
                        company_name=company_name,
                        tier=tier,
                        job_title=title_text,
                        location=location,
                        job_url=job_url,
                        description=description,
                        source="career_page",
                    )
                )
                self._logger.info(
                    "  [green]→[/] Matched: [bold]%s[/] @ %s", title_text, location
                )

        finally:
            await context.close()

        return listings

    # ══════════════════════════════════════════════════════════════════════
    # GREENHOUSE — boards.greenhouse.io/<company>
    # ══════════════════════════════════════════════════════════════════════
    # Greenhouse boards list jobs in department sections, each job is an
    # <a> inside a <div class="opening">.

    async def _scrape_greenhouse(
        self, company_name: str, tier: str, target_url: str
    ) -> list[JobListing]:
        """Extract job listings from a Greenhouse job board."""
        context = await self._create_context()
        listings: list[JobListing] = []

        try:
            page = await context.new_page()
            html = await self._navigate_and_wait(page, target_url)
            soup = BeautifulSoup(html, "lxml")

            # Greenhouse structure:
            #   <div class="opening">
            #     <a href="/company/jobs/12345">Job Title</a>
            #     <span class="location">City, Country</span>
            #   </div>
            openings = soup.select("div.opening, tr.job-post")
            self._logger.info("Greenhouse: found %d total openings", len(openings))

            for opening in openings:
                link_tag = opening.select_one("a")
                if not link_tag:
                    continue

                title_text = link_tag.get_text(strip=True)

                if not _TITLE_PATTERN.search(title_text):
                    continue

                location_tag = opening.select_one("span.location, td.location")
                location = location_tag.get_text(strip=True) if location_tag else ""

                if not _LOCATION_PATTERN.search(location):
                    continue

                job_url = self.make_absolute_url(target_url, link_tag.get("href", ""))

                await self._random_delay()
                description = await self._fetch_job_description(
                    context, job_url, platform="greenhouse"
                )

                listings.append(
                    JobListing(
                        company_name=company_name,
                        tier=tier,
                        job_title=title_text,
                        location=location,
                        job_url=job_url,
                        description=description,
                        source="career_page",
                    )
                )
                self._logger.info(
                    "  [green]→[/] Matched: [bold]%s[/] @ %s", title_text, location
                )

        finally:
            await context.close()

        return listings

    # ══════════════════════════════════════════════════════════════════════
    # WORKDAY — *.myworkdayjobs.com
    # ══════════════════════════════════════════════════════════════════════
    # Workday is the most challenging platform — it's a full SPA with
    # shadow DOM elements and dynamic loading.  We rely on waiting for
    # specific selectors to appear.

    async def _scrape_workday(
        self, company_name: str, tier: str, target_url: str
    ) -> list[JobListing]:
        """Extract job listings from a Workday career site."""
        context = await self._create_context()
        listings: list[JobListing] = []

        try:
            page = await context.new_page()
            html = await self._navigate_and_wait(page, target_url)

            # Workday often needs extra time for its SPA to hydrate.
            # Try to wait for a common Workday job list selector.
            try:
                await page.wait_for_selector(
                    'section[data-automation-id="jobResults"], '
                    'ul[role="list"], '
                    'div.css-1q2dra3',  # common Workday result container
                    timeout=10000,
                )
            except PlaywrightTimeoutError:
                self._logger.warning(
                    "Workday job results container not found — parsing available HTML"
                )

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            # Workday job links typically contain the job title as link text
            # and have hrefs matching /job/<id> or /en-US/job/<id>
            all_links = soup.find_all("a", href=True)
            self._logger.info("Workday: scanning %d links", len(all_links))

            seen_urls: set[str] = set()

            for link in all_links:
                href = link.get("href", "")
                text = link.get_text(strip=True)

                # Workday job links typically contain "/job/" in the path
                if "/job/" not in href.lower() and "/jobs/" not in href.lower():
                    continue

                if not text or not _TITLE_PATTERN.search(text):
                    continue

                job_url = self.make_absolute_url(target_url, href)
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # For Workday, location is often in a sibling or parent element.
                # Look in the surrounding container for location text.
                location = self._extract_workday_location(link)

                if location and not _LOCATION_PATTERN.search(location):
                    continue

                await self._random_delay()
                description = await self._fetch_job_description(
                    context, job_url, platform="workday"
                )

                # If we couldn't get location from the list page, try the detail page
                if not location:
                    location = self._extract_location_from_text(description)

                # Final location check after trying all sources
                if not _LOCATION_PATTERN.search(location):
                    continue

                listings.append(
                    JobListing(
                        company_name=company_name,
                        tier=tier,
                        job_title=text,
                        location=location,
                        job_url=job_url,
                        description=description,
                        source="career_page",
                    )
                )
                self._logger.info(
                    "  [green]→[/] Matched: [bold]%s[/] @ %s", text, location
                )

        finally:
            await context.close()

        return listings

    # ══════════════════════════════════════════════════════════════════════
    # GENERIC — any custom career page
    # ══════════════════════════════════════════════════════════════════════
    # This is the catch-all strategy: find all links on the page, filter
    # by title keywords, then visit each match for the full description.
    # It's less precise than platform-specific parsers but works on most
    # career pages that list jobs as plain HTML links.

    async def _scrape_generic(
        self, company_name: str, tier: str, target_url: str
    ) -> list[JobListing]:
        """Extract job listings from an unrecognised career page layout."""
        context = await self._create_context()
        listings: list[JobListing] = []

        try:
            page = await context.new_page()
            html = await self._navigate_and_wait(page, target_url)
            soup = BeautifulSoup(html, "lxml")

            # Strategy: find ALL anchor tags, then filter by title keywords.
            # This is broad by design — false positives are filtered out by
            # the scoring engine downstream.
            all_links = soup.find_all("a", href=True)
            self._logger.info("Generic: scanning %d links on page", len(all_links))

            # Also check headings and list items that might contain job info
            # (some pages use <li> or <div> wrappers around job cards)
            job_cards = soup.select(
                "[class*='job'], [class*='position'], [class*='opening'], "
                "[class*='career'], [class*='role'], [class*='vacancy'], "
                "[data-job], [data-role], li[class*='list']"
            )
            self._logger.info("Generic: found %d potential job cards", len(job_cards))

            # Merge links from both sources
            candidate_links: list[tuple[str, str, str]] = []  # (title, url, location)
            seen_urls: set[str] = set()

            # From direct <a> tags
            for link in all_links:
                text = link.get_text(strip=True)
                href = link.get("href", "")

                if not text or len(text) < 5 or len(text) > 200:
                    continue

                if not _TITLE_PATTERN.search(text):
                    continue

                job_url = self.make_absolute_url(target_url, href)
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # Try to find location near the link
                location = self._extract_nearby_location(link)
                candidate_links.append((text, job_url, location))

            # From job card containers (look for links within them)
            for card in job_cards:
                card_link = card.select_one("a[href]")
                if not card_link:
                    continue

                text = card_link.get_text(strip=True)
                href = card_link.get("href", "")

                if not text or not _TITLE_PATTERN.search(text):
                    # Also check the card's full text
                    card_text = card.get_text(strip=True)
                    if not _TITLE_PATTERN.search(card_text):
                        continue
                    text = card_text[:150]  # truncate to reasonable title length

                job_url = self.make_absolute_url(target_url, href)
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                location = self._extract_nearby_location(card)
                candidate_links.append((text, job_url, location))

            self._logger.info(
                "Generic: %d candidates after title-keyword filtering",
                len(candidate_links),
            )

            # ── Visit each candidate's detail page ───────────────────────
            for title_text, job_url, location in candidate_links:
                # Pre-filter by location if we already have it
                if location and not _LOCATION_PATTERN.search(location):
                    continue

                await self._random_delay()
                description = await self._fetch_job_description(
                    context, job_url, platform="generic"
                )

                # If location wasn't on the list page, extract from description
                if not location:
                    location = self._extract_location_from_text(description)

                # Final location gate
                if not _LOCATION_PATTERN.search(location):
                    continue

                listings.append(
                    JobListing(
                        company_name=company_name,
                        tier=tier,
                        job_title=title_text,
                        location=location,
                        job_url=job_url,
                        description=description,
                        source="career_page",
                    )
                )
                self._logger.info(
                    "  [green]→[/] Matched: [bold]%s[/] @ %s", title_text, location
                )

        finally:
            await context.close()

        return listings

    # ══════════════════════════════════════════════════════════════════════
    # Shared extraction helpers
    # ══════════════════════════════════════════════════════════════════════

    async def _fetch_job_description(
        self, context: BrowserContext, job_url: str, platform: str
    ) -> str:
        """
        Navigate to a job detail page and extract the full description text.

        Opens a new page within the existing context (shares cookies),
        waits for it to render, then extracts text using platform-specific
        selectors with a generic fallback.

        The page is always closed in the finally block.

        Args:
            context:  The existing browser context.
            job_url:  URL of the job detail page.
            platform: One of "lever", "greenhouse", "workday", "generic".

        Returns:
            The extracted plain-text job description, or empty string on failure.
        """
        page: Optional[Page] = None
        try:
            page = await context.new_page()
            html = await self._navigate_and_wait(page, job_url)
            soup = BeautifulSoup(html, "lxml")

            description = ""

            # ── Platform-specific selectors ──────────────────────────────
            if platform == "lever":
                # Lever puts the JD in a <div class="section-wrapper page-centered">
                # with <div class="content"> children
                content = soup.select_one(
                    "div.section-wrapper.page-centered, "
                    "div.content, "
                    "div[class*='posting-page']"
                )
                if content:
                    description = content.get_text(separator="\n", strip=True)

            elif platform == "greenhouse":
                # Greenhouse uses <div id="content"> or <div class="job-post">
                content = soup.select_one(
                    "div#content, div.job-post, div#app_body, section.job-description"
                )
                if content:
                    description = content.get_text(separator="\n", strip=True)

            elif platform == "workday":
                # Workday wraps the JD in a <div data-automation-id="jobPostingDescription">
                content = soup.select_one(
                    'div[data-automation-id="jobPostingDescription"], '
                    "div.css-kyg8or, "
                    "div[class*='jobDescription']"
                )
                if content:
                    description = content.get_text(separator="\n", strip=True)

            # ── Generic fallback ─────────────────────────────────────────
            if not description:
                # Try common job description containers
                for selector in [
                    "div.job-description",
                    "div.jd-info",
                    "div[class*='description']",
                    "div[class*='job-detail']",
                    "article",
                    "main",
                    "div.content",
                    "div#content",
                ]:
                    content = soup.select_one(selector)
                    if content and len(content.get_text(strip=True)) > 100:
                        description = content.get_text(separator="\n", strip=True)
                        break

            # ── Last resort: use the whole <body> ────────────────────────
            if not description:
                body = soup.find("body")
                if body:
                    description = body.get_text(separator="\n", strip=True)

            # Trim to a reasonable length (some pages include nav/footer noise)
            if len(description) > 10000:
                description = description[:10000]

            return description

        except Exception as exc:
            self._logger.warning(
                "Failed to fetch description from %s: %s", job_url, exc
            )
            return ""

        finally:
            # Always close the detail page to free memory
            if page:
                await page.close()

    @staticmethod
    def _extract_nearby_location(tag: Tag) -> str:
        """
        Look for location text near a job link element.

        Career pages typically put the location in a sibling element,
        a parent container, or a dedicated <span> nearby.  We scan
        the surrounding HTML for common location patterns.
        """
        # Strategy 1: look in siblings with location-related classes
        parent = tag.parent
        if parent:
            for selector in [
                "[class*='location']",
                "[class*='city']",
                "[class*='place']",
                "[data-field='location']",
                "span.meta",
                "span.subtitle",
            ]:
                loc_tag = parent.select_one(selector)
                if loc_tag:
                    text = loc_tag.get_text(strip=True)
                    if text and len(text) < 100:
                        return text

            # Strategy 2: look at grandparent
            grandparent = parent.parent
            if grandparent:
                for selector in ["[class*='location']", "[class*='city']"]:
                    loc_tag = grandparent.select_one(selector)
                    if loc_tag:
                        text = loc_tag.get_text(strip=True)
                        if text and len(text) < 100:
                            return text

        return ""

    @staticmethod
    def _extract_workday_location(link: Tag) -> str:
        """
        Extract location from a Workday job listing element.

        Workday uses deeply nested structures.  We walk up to the
        nearest list-item or card container and search for location info.
        """
        # Walk up to 5 levels to find a container
        current = link
        for _ in range(5):
            parent = current.parent
            if not parent:
                break
            current = parent

            # Look for elements with location-related data attributes or classes
            for selector in [
                'dd[class*="location"], [data-automation-id="locations"]',
                '[class*="location"], [class*="Location"]',
            ]:
                loc_tag = current.select_one(selector)
                if loc_tag:
                    text = loc_tag.get_text(strip=True)
                    if text and len(text) < 100:
                        return text

        return ""

    @staticmethod
    def _extract_location_from_text(text: str) -> str:
        """
        Extract a location string from free-form text (e.g., a JD body).

        Uses regex to find patterns like "Location: Bengaluru, India" or
        "Office: Hyderabad" within the description text.
        """
        if not text:
            return ""

        # Pattern 1: "Location: City" or "Office: City"
        loc_match = re.search(
            r"(?:location|office|based in|city)\s*[:\-–]\s*([^\n]{3,60})",
            text,
            re.IGNORECASE,
        )
        if loc_match:
            candidate = loc_match.group(1).strip()
            if _LOCATION_PATTERN.search(candidate):
                return candidate

        # Pattern 2: Just look for the city name in context
        for city in TARGET_LOCATIONS:
            pattern = re.compile(
                rf"(?:^|\W)({re.escape(city)}[\w\s,]*?)(?:\.|,|\n|$)",
                re.IGNORECASE,
            )
            match = pattern.search(text)
            if match:
                return match.group(1).strip()[:60]

        return ""

    # ── Cleanup ──────────────────────────────────────────────────────────

    async def _cleanup(self) -> None:
        """
        Close browser and Playwright, handling errors gracefully.

        Called in the finally block of _do_scrape to ensure no
        Chromium processes are left running.
        """
        try:
            if self._browser:
                await self._browser.close()
                self._logger.debug("Browser closed.")
        except Exception as exc:
            self._logger.warning("Error closing browser: %s", exc)

        try:
            if self._playwright:
                await self._playwright.stop()
                self._logger.debug("Playwright stopped.")
        except Exception as exc:
            self._logger.warning("Error stopping Playwright: %s", exc)

        self._browser = None
        self._playwright = None
