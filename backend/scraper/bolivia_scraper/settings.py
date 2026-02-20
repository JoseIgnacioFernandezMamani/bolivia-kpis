"""Crawlee-based scraper configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

# Identity
BOT_NAME = "BoliviaKPIs"
USER_AGENT: str = os.getenv("SCRAPER_USER_AGENT", "BoliviaKPIs/1.0 (+https://github.com/JoseIgnacioFernandezMamani/bolivia-kpis)")

# Crawlee Configuration
MAX_REQUESTS_PER_CRAWL: int = int(os.getenv("MAX_REQUESTS_PER_CRAWL", "0"))  # 0 = unlimited
MAX_REQUEST_RETRIES: int = int(os.getenv("MAX_REQUEST_RETRIES", "3"))
MAX_CONCURRENCY: int = int(os.getenv("MAX_CONCURRENCY", "4"))
MIN_CONCURRENCY: int = int(os.getenv("MIN_CONCURRENCY", "1"))
REQUEST_HANDLER_TIMEOUT_SECS: int = int(os.getenv("REQUEST_HANDLER_TIMEOUT_SECS", "60"))

# Browser settings
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
BROWSER_TYPE: str = os.getenv("BROWSER_TYPE", "chromium")  # chromium, firefox, webkit
NAVIGATION_TIMEOUT_MS: int = int(os.getenv("NAVIGATION_TIMEOUT_MS", "45000"))

# Storage
DATA_RAW_DIR: str = os.getenv(
    "DATA_RAW_DIR",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw"),
)
CRAWLEE_STORAGE_DIR: str = os.getenv(
    "CRAWLEE_STORAGE_DIR",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "storage"),
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
