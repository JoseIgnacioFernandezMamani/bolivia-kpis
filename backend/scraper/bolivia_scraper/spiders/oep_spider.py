"""
OEP (Órgano Electoral Plurinacional) election results spider using Crawlee.
"""
import logging
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext

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


class OEPElectionsSpider:
    """Crawlee-based spider for OEP election results."""

    name = NAME

    def __init__(self) -> None:
        self.results: list[ElectionResultItem] = []
        self._visited_election_pages: set[str] = set()

    async def run(self) -> list[ElectionResultItem]:
        """Run the crawler and return scraped items."""
        crawler = PlaywrightCrawler(
            max_requests_per_crawl=settings.MAX_REQUESTS_PER_CRAWL or None,
            max_request_retries=settings.MAX_REQUEST_RETRIES,
            max_concurrency=settings.MAX_CONCURRENCY,
            min_concurrency=settings.MIN_CONCURRENCY,
            request_handler_timeout_secs=settings.REQUEST_HANDLER_TIMEOUT_SECS,
            headless=settings.HEADLESS,
            browser_type=settings.BROWSER_TYPE,
        )

        @crawler.router.default_handler
        async def handle_index(context: PlaywrightCrawlingContext) -> None:
            """Handle index pages and discover election event links."""
            await context.page.wait_for_load_state("networkidle")
            await context.page.wait_for_timeout(1500)

            # Expand collapsible sections
            for selector in ["button.accordion", ".tab-link", "[data-toggle='collapse']"]:
                buttons = await context.page.query_selector_all(selector)
                for btn in buttons:
                    try:
                        await btn.click()
                        await context.page.wait_for_timeout(300)
                    except Exception:
                        pass

            html = await context.page.content()
            soup = BeautifulSoup(html, "lxml")

            logger.info(f"Processing index: {context.request.url}")

            # Find election event links
            links_added = 0
            for a in soup.find_all("a", href=True):
                href: str = a["href"]
                text: str = a.get_text(strip=True)
                combined = href + " " + text

                # Only follow links that mention years
                if not (re.search(r"\b(19|20)\d{2}\b", href) or re.search(r"\b(19|20)\d{2}\b", text)):
                    continue

                full_url = urljoin(str(context.request.url), href)
                
                if full_url not in self._visited_election_pages:
                    self._visited_election_pages.add(full_url)
                    election_type = _classify_election_type(combined)
                    
                    # Enqueue for election page handler
                    await context.add_requests([
                        {
                            "url": full_url,
                            "label": "election_page",
                            "user_data": {"election_type": election_type},
                        }
                    ])
                    links_added += 1

            logger.info(f"Added {links_added} election page URLs from {context.request.url}")

        @crawler.router.handler("election_page")
        async def handle_election_page(context: PlaywrightCrawlingContext) -> None:
            """Handle individual election event pages and extract tables."""
            await context.page.wait_for_load_state("networkidle")
            await context.page.wait_for_timeout(1500)

            # Expand collapsible sections
            for selector in ["button.accordion", ".tab-link", "[data-toggle='collapse']"]:
                buttons = await context.page.query_selector_all(selector)
                for btn in buttons:
                    try:
                        await btn.click()
                        await context.page.wait_for_timeout(300)
                    except Exception:
                        pass

            html = await context.page.content()
            soup = BeautifulSoup(html, "lxml")
            
            url = str(context.request.url)
            election_type = context.request.user_data.get("election_type", "general")
            
            logger.info(f"Processing election page: {url}")

            # Extract year from URL and title
            title_text = " ".join(t.get_text() for t in soup.find_all(["h1", "h2"]))
            year = _extract_year(url + " " + title_text)

            # Extract all tables
            items_count = 0
            for table in soup.find_all("table"):
                items = _parse_results_table(str(table), year, election_type, url)
                self.results.extend(items)
                items_count += len(items)

            logger.info(f"Extracted {items_count} items from {url}")

            # Follow pagination links
            for a in soup.find_all("a", class_=re.compile(r"next|siguiente"), href=True):
                next_url = urljoin(url, a["href"])
                if next_url not in self._visited_election_pages:
                    self._visited_election_pages.add(next_url)
                    await context.add_requests([
                        {
                            "url": next_url,
                            "label": "election_page",
                            "user_data": {"election_type": election_type},
                        }
                    ])

        # Run the crawler
        await crawler.run(START_URLS)
        
        logger.info(f"OEP spider finished – {len(self.results)} items scraped")
        return self.results
