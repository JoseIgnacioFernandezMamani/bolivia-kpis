"""Entry point for Crawlee-based scraper: python -m bolivia_scraper [spider_name]

Usage:
    python -m bolivia_scraper              # run all spiders
    python -m bolivia_scraper oep_elections
"""
import asyncio
import logging
import sys
import os

from bolivia_scraper import settings
from bolivia_scraper.pipelines import run_pipelines

# Set Crawlee storage directory
os.environ["CRAWLEE_STORAGE_DIR"] = settings.CRAWLEE_STORAGE_DIR

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

# Registry: spider name → spider class
_SPIDERS: dict[str, type] = {}

try:
    from bolivia_scraper.spiders.oep_spider import OEPElectionsSpider

    _SPIDERS[OEPElectionsSpider.name] = OEPElectionsSpider
except ImportError as exc:
    logger.warning("Could not import OEPElectionsSpider: %s", exc)


async def _run_spider(name: str) -> None:
    cls = _SPIDERS.get(name)
    if cls is None:
        logger.error("Unknown spider: %r. Available: %s", name, list(_SPIDERS))
        sys.exit(1)
    spider = cls()
    items = await spider.run()
    saved = run_pipelines(name, items)
    logger.info("Spider %r: %d items scraped, %d saved after deduplication", name, len(items), saved)


async def _run_all() -> None:
    for name in _SPIDERS:
        await _run_spider(name)


def main() -> None:
    if not _SPIDERS:
        logger.error("No spiders registered – aborting.")
        sys.exit(1)

    if len(sys.argv) >= 2:
        asyncio.run(_run_spider(sys.argv[1]))
    else:
        asyncio.run(_run_all())


if __name__ == "__main__":
    main()
