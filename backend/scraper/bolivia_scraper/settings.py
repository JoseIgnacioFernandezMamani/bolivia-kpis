import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "bolivia_scraper"
SPIDER_MODULES = ["bolivia_scraper.spiders"]
NEWSPIDER_MODULE = "bolivia_scraper.spiders"

# Obey robots.txt
ROBOTSTXT_OBEY = True

# Crawl responsibly
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

USER_AGENT = os.getenv("SCRAPER_USER_AGENT", "BoliviaKPIs/1.0")

# Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30_000  # ms

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Pipelines
ITEM_PIPELINES = {
    "bolivia_scraper.pipelines.HashCheckPipeline": 100,
    "bolivia_scraper.pipelines.JsonExportPipeline": 200,
    "bolivia_scraper.pipelines.DatabasePipeline": 300,
}

# Redis connection (for change-detection hashes)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Output dir
DATA_RAW_DIR = os.getenv("DATA_RAW_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw"))

# Logging
LOG_LEVEL = "INFO"

# Retry
RETRY_ENABLED = True
RETRY_TIMES = 3

# Autothrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
