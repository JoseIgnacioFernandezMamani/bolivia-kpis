"""
Spider for OEP (Órgano Electoral Plurinacional) election results.
Uses Playwright to handle JavaScript-rendered pages.
"""
import re
from datetime import datetime, timezone
from typing import Generator

import scrapy
from scrapy_playwright.page import PageMethod

from bolivia_scraper.items import ElectionResultItem


class OEPElectionsSpider(scrapy.Spider):
    name = "oep_elections"
    allowed_domains = ["oep.org.bo"]

    # Entry points – one per election type known to be on the OEP site
    start_urls = [
        "https://www.oep.org.bo/proceso-electoral/elecciones-generales/",
        "https://www.oep.org.bo/proceso-electoral/elecciones-departamentales-y-municipales/",
        "https://www.oep.org.bo/proceso-electoral/referendos/",
    ]

    # Map Spanish election-type labels to canonical names
    _ELECTION_TYPE_MAP = {
        "generales": "general",
        "departamentales": "departmental",
        "municipales": "municipal",
        "referendo": "referendum",
        "subnacionales": "subnational",
    }

    # Bolivia's 9 departments
    _DEPARTMENTS = {
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

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 45_000,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": True,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                },
                callback=self.parse_election_index,
                errback=self.errback,
            )

    async def parse_election_index(self, response) -> Generator:
        """Parse the index page listing individual election years/events."""
        page = response.meta.get("playwright_page")
        if page:
            await page.close()

        # Look for links that contain year-specific election pages
        for link in response.css("a[href]"):
            href = link.attrib.get("href", "")
            text = link.css("::text").get("").strip().lower()

            # Match links that look like election event entries (contain 4-digit year)
            if re.search(r"\b(19|20)\d{2}\b", href) or re.search(r"\b(19|20)\d{2}\b", text):
                yield response.follow(
                    href,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "networkidle"),
                            PageMethod("wait_for_timeout", 2000),
                        ],
                        "election_type_hint": self._classify_election_type(href + " " + text),
                    },
                    callback=self.parse_election_page,
                    errback=self.errback,
                )

    async def parse_election_page(self, response) -> Generator:
        """Parse a single election-event page that may contain results tables."""
        page = response.meta.get("playwright_page")
        election_type_hint = response.meta.get("election_type_hint", "general")

        try:
            if page:
                # Attempt to expand any collapsed accordion/tab sections
                try:
                    expand_buttons = await page.query_selector_all("button.accordion, .tab-link, [data-toggle='collapse']")
                    for btn in expand_buttons:
                        try:
                            await btn.click()
                            await page.wait_for_timeout(500)
                        except Exception:
                            pass
                except Exception:
                    pass

                # Re-read the fully rendered HTML
                content = await page.content()
                response = response.replace(body=content.encode())
        finally:
            if page:
                await page.close()

        # Extract year from URL or page title
        year = self._extract_year(response.url + " " + response.css("h1::text, h2::text").get(""))

        # Parse result tables
        for table in response.css("table"):
            yield from self._parse_results_table(table, year, election_type_hint, response.url)

        # Follow pagination
        for next_page in response.css("a.next, a[rel='next'], .pagination a[href]"):
            yield response.follow(
                next_page,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                    "election_type_hint": election_type_hint,
                },
                callback=self.parse_election_page,
                errback=self.errback,
            )

    def _parse_results_table(self, table, year, election_type, source_url) -> Generator:
        """Extract election result rows from an HTML table."""
        headers = [th.css("::text").get("").strip().lower() for th in table.css("tr:first-child th, tr:first-child td")]

        col_map = {}
        for i, h in enumerate(headers):
            if any(k in h for k in ["partido", "organización", "sigla"]):
                col_map["party"] = i
            elif any(k in h for k in ["candidato", "nombre"]):
                col_map["candidate"] = i
            elif any(k in h for k in ["votos", "total"]):
                col_map["votes"] = i
            elif "%" in h or "porcentaje" in h:
                col_map["percentage"] = i
            elif any(k in h for k in ["departamento", "circunscripción", "municipio"]):
                col_map["department"] = i

        if not col_map:
            return

        for row in table.css("tr")[1:]:
            cells = row.css("td")
            if len(cells) < 2:
                continue

            def _cell(key):
                idx = col_map.get(key)
                if idx is None or idx >= len(cells):
                    return None
                return cells[idx].css("::text").get("").strip() or None

            votes_raw = _cell("votes")
            percentage_raw = _cell("percentage")

            try:
                votes = int(re.sub(r"\D", "", votes_raw)) if votes_raw else None
            except ValueError:
                votes = None

            try:
                percentage = float(re.sub(r"[^\d.]", "", percentage_raw)) if percentage_raw else None
            except ValueError:
                percentage = None

            department_raw = _cell("department") or ""
            department = self._DEPARTMENTS.get(department_raw.lower(), department_raw or None)

            item = ElectionResultItem(
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
            yield item

    @staticmethod
    def _extract_year(text: str) -> int | None:
        m = re.search(r"\b(19|20)(\d{2})\b", text)
        if m:
            return int(m.group(0))
        return None

    def _classify_election_type(self, text: str) -> str:
        text_lower = text.lower()
        for keyword, canonical in self._ELECTION_TYPE_MAP.items():
            if keyword in text_lower:
                return canonical
        return "general"

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error("Request failed: %s", failure)
