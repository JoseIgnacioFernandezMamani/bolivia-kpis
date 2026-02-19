"""Scraper configuration – plain os.getenv (no Scrapy dependency)."""
import os
from dotenv import load_dotenv

load_dotenv()

# Identity
BOT_NAME = "BoliviaKPIs"
USER_AGENT: str = os.getenv("SCRAPER_USER_AGENT", "BoliviaKPIs/1.0 (+https://github.com/JoseIgnacioFernandezMamani/bolivia-kpis)")

# Politeness
DOWNLOAD_DELAY: float = float(os.getenv("DOWNLOAD_DELAY", "2"))
CONCURRENT_REQUESTS: int = int(os.getenv("CONCURRENT_REQUESTS", "4"))
NAVIGATION_TIMEOUT_MS: int = int(os.getenv("NAVIGATION_TIMEOUT_MS", "45000"))
OBEY_ROBOTS_TXT: bool = os.getenv("OBEY_ROBOTS_TXT", "true").lower() == "true"

# Retry
RETRY_TIMES: int = int(os.getenv("RETRY_TIMES", "3"))

# Browser
PLAYWRIGHT_BROWSER_TYPE: str = os.getenv("PLAYWRIGHT_BROWSER_TYPE", "chromium")
PLAYWRIGHT_HEADLESS: bool = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"

# Storage
DATA_RAW_DIR: str = os.getenv(
    "DATA_RAW_DIR",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw"),
)

# Redis (change-detection hashes)
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
HASH_TTL_SECONDS: int = int(os.getenv("HASH_TTL_SECONDS", str(60 * 60 * 24 * 30)))  # 30 days

# Database
DATABASE_SYNC_URL: str = os.getenv(
    "DATABASE_SYNC_URL",
    "postgresql+psycopg2://bolivia:bolivia@localhost:5432/bolivia_kpis",
)

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
