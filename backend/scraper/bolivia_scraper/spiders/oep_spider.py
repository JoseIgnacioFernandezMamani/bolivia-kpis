"""
Standalone async spider for OEP (Órgano Electoral Plurinacional) election results.
Uses Playwright directly – no Scrapy dependency.
"""
import asyncio
import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page

from bolivia_scraper import settings
from bolivia_scraper.items import ElectionResultItem

logger = logging.getLogger(__name__)

# Bolivia's 9 departments
_DEPARTMENTS: dict[str, Optional[str]] = {
    "la paz": "La Paz",
    "cochabamba": "Cochabamba",
    "santa cruz": "Santa Cruz",
    "oruro": "Oruro",
    "potosí": "Potosí",
    "potosi": "Potosí",
    "chuquisaca": "Chuquisaca",
    "tarija": "Tarija",
    "beni": "Beni",
    "pando": "Pando",
    "nacional": None,
}

_ELECTION_TYPE_MAP: dict[str, str] = {
    "generales": "general",
    "departamentales": "departmental",
    "municipales": "municipal",
    "referendo": "referendum",
    "subnacionales": "subnational",
}

START_URLS = [
    "https://www.oep.org.bo/proceso-electoral/elecciones-generales/",
    "https://www.oep.org.bo/proceso-electoral/elecciones-departamentales-y-municipales/",
    "https://www.oep.org.bo/proceso-electoral/referendos/",
]

NAME = "oep_elections"


def _classify_election_type(text: str) -> str:
    text_lower = text.lower()
    for keyword, canonical in _ELECTION_TYPE_MAP.items():
        if keyword in text_lower:
            return canonical
    return "general"


def _extract_year(text: str) -> Optional[int]:
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group(0)) if m else None


def _parse_results_table(
    table_html: str,
    year: Optional[int],
    election_type: str,
    source_url: str,
) -> list[ElectionResultItem]:
    """Extract election-result rows from an HTML <table>."""
    soup = BeautifulSoup(table_html, "lxml")
    rows = soup.find_all("tr")
    if not rows:
        return []

    # Identify columns from the first header row
    headers = [
        cell.get_text(strip=True).lower()
        for cell in rows[0].find_all(["th", "td"])
    ]
    col: dict[str, int] = {}
    for i, h in enumerate(headers):
        if any(k in h for k in ["partido", "organización", "sigla"]):
            col.setdefault("party", i)
        elif any(k in h for k in ["candidato", "nombre"]):
            col.setdefault("candidate", i)
        elif any(k in h for k in ["votos", "total"]):
            col.setdefault("votes", i)
        elif "%" in h or "porcentaje" in h:
            col.setdefault("percentage", i)
        elif any(k in h for k in ["departamento", "circunscripción", "municipio"]):
            col.setdefault("department", i)

    if not col:
        return []

    items: list[ElectionResultItem] = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        def _cell(key: str) -> Optional[str]:
            idx = col.get(key)
            if idx is None or idx >= len(cells):
                return None
            return cells[idx].get_text(strip=True) or None

        votes_raw = _cell("votes")
        pct_raw = _cell("percentage")
        try:
            votes = int(re.sub(r"\D", "", votes_raw)) if votes_raw else None
        except ValueError:
            votes = None
        try:
            percentage = float(re.sub(r"[^\d.]", "", pct_raw)) if pct_raw else None
        except ValueError:
            percentage = None

        dept_raw = _cell("department") or ""
        department = _DEPARTMENTS.get(dept_raw.lower(), dept_raw or None)

        items.append(
            ElectionResultItem(
                year=year,
                election_type=election_type,
                department=department,
                party=_cell("party"),
                candidate=_cell("candidate"),
                votes=votes,
                percentage=percentage,
                source_url=source_url,
                scraped_at=datetime.now(timezone.utc).isoformat(),
            )
        )
    return items


def _is_allowed(url: str, user_agent: str) -> bool:
    """Check robots.txt for the given URL."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True  # assume allowed on fetch failure
    return rp.can_fetch(user_agent, url)


async def _fetch_with_playwright(
    browser: Browser,
    url: str,
    user_agent: str,
    navigation_timeout: int,
) -> str:
    """Load a URL in a new browser page and return fully-rendered HTML."""
    context = await browser.new_context(user_agent=user_agent)
    page: Page = await context.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=navigation_timeout)
        await page.wait_for_timeout(1500)

        # Expand any collapsible sections
        for selector in ["button.accordion", ".tab-link", "[data-toggle='collapse']"]:
            try:
                buttons = await page.query_selector_all(selector)
                for btn in buttons:
                    try:
                        await btn.click()
                        await page.wait_for_timeout(300)
                    except Exception:
                        pass
            except Exception:
                pass

        return await page.content()
    finally:
        await page.close()
        await context.close()


class OEPElectionsSpider:
    """Async spider that crawls OEP election-results pages."""

    name = NAME

    def __init__(self) -> None:
        self._visited: set[str] = set()

    async def run(self) -> list[ElectionResultItem]:
        results: list[ElectionResultItem] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
            try:
                for start_url in START_URLS:
                    if not settings.OBEY_ROBOTS_TXT or _is_allowed(start_url, settings.USER_AGENT):
                        index_items = await self._crawl_index(browser, start_url)
                        results.extend(index_items)
            finally:
                await browser.close()

        logger.info("OEP spider finished – %d items scraped", len(results))
        return results

    async def _crawl_index(self, browser: Browser, url: str) -> list[ElectionResultItem]:
        """Fetch an index page and follow election-event links."""
        logger.info("Fetching index: %s", url)
        try:
            html = await _fetch_with_playwright(
                browser, url, settings.USER_AGENT, settings.NAVIGATION_TIMEOUT_MS
            )
        except Exception as exc:
            logger.error("Failed to load index %s: %s", url, exc)
            return []

        soup = BeautifulSoup(html, "lxml")
        items: list[ElectionResultItem] = []

        for a in soup.find_all("a", href=True):
            href: str = a["href"]
            text: str = a.get_text(strip=True)
            combined = href + " " + text

            if not (re.search(r"\b(19|20)\d{2}\b", href) or re.search(r"\b(19|20)\d{2}\b", text)):
                continue

            full_url = urljoin(url, href)
            if full_url in self._visited:
                continue
            if settings.OBEY_ROBOTS_TXT and not _is_allowed(full_url, settings.USER_AGENT):
                continue

            self._visited.add(full_url)
            election_type = _classify_election_type(combined)

            await asyncio.sleep(settings.DOWNLOAD_DELAY)
            page_items = await self._crawl_election_page(browser, full_url, election_type)
            items.extend(page_items)

        return items

    async def _crawl_election_page(
        self, browser: Browser, url: str, election_type: str
    ) -> list[ElectionResultItem]:
        """Fetch a single election-event page and extract all result tables."""
        logger.info("Fetching election page: %s", url)
        items: list[ElectionResultItem] = []

        for attempt in range(1, settings.RETRY_TIMES + 1):
            try:
                html = await _fetch_with_playwright(
                    browser, url, settings.USER_AGENT, settings.NAVIGATION_TIMEOUT_MS
                )
                break
            except Exception as exc:
                logger.warning("Attempt %d/%d failed for %s: %s", attempt, settings.RETRY_TIMES, url, exc)
                if attempt == settings.RETRY_TIMES:
                    return []
                await asyncio.sleep(settings.DOWNLOAD_DELAY * attempt)

        soup = BeautifulSoup(html, "lxml")
        title_text = " ".join(t.get_text() for t in soup.find_all(["h1", "h2"]))
        year = _extract_year(url + " " + title_text)

        for table in soup.find_all("table"):
            items.extend(_parse_results_table(str(table), year, election_type, url))

        # Follow pagination links
        for a in soup.find_all("a", class_=re.compile(r"next|siguiente"), href=True):
            next_url = urljoin(url, a["href"])
            if next_url not in self._visited:
                self._visited.add(next_url)
                await asyncio.sleep(settings.DOWNLOAD_DELAY)
                items.extend(await self._crawl_election_page(browser, next_url, election_type))

        return items
