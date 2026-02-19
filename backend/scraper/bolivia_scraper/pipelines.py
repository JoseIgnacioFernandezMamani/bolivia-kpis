"""Scrapy item pipelines."""
import hashlib
import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import redis as redis_lib
import psycopg2
from scrapy import Spider
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


def _item_hash(item: dict) -> str:
    """Return SHA-256 hex digest of deterministic JSON representation."""
    canonical = json.dumps(item, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


class HashCheckPipeline:
    """Drop items whose content hash has not changed since last run."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: redis_lib.Redis | None = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(redis_url=crawler.settings.get("REDIS_URL", "redis://localhost:6379/0"))

    def open_spider(self, spider: Spider):
        try:
            self.redis = redis_lib.from_url(self.redis_url, decode_responses=True)
            self.redis.ping()
        except Exception as exc:
            logger.warning("Redis unavailable – hash check disabled: %s", exc)
            self.redis = None

    def process_item(self, item: Any, spider: Spider):
        if self.redis is None:
            return item

        d = dict(item)
        d.pop("scraped_at", None)
        key = f"hash:{spider.name}:{_item_hash(d)}"

        if self.redis.get(key):
            raise DropItem(f"Unchanged item – skipping: {d.get('sicoes_id') or d.get('title', '')}")

        self.redis.set(key, "1", ex=60 * 60 * 24 * 30)  # expire after 30 days
        return item


class JsonExportPipeline:
    """Append each item to a JSONL file under data/raw/<spider_name>.jsonl"""

    def __init__(self, raw_dir: str):
        self.raw_dir = Path(raw_dir)
        self._handles: dict[str, Any] = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(raw_dir=crawler.settings.get("DATA_RAW_DIR", "data/raw"))

    def open_spider(self, spider: Spider):
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def close_spider(self, spider: Spider):
        for fh in self._handles.values():
            fh.close()

    def process_item(self, item: Any, spider: Spider):
        key = spider.name
        if key not in self._handles:
            path = self.raw_dir / f"{key}.jsonl"
            self._handles[key] = open(path, "a", encoding="utf-8")
        line = json.dumps(dict(item), default=str)
        self._handles[key].write(line + "\n")
        return item


class DatabasePipeline:
    """Upsert election results into PostgreSQL."""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        self.cur = None

    @classmethod
    def from_crawler(cls, crawler):
        db_url = os.getenv("DATABASE_SYNC_URL", "postgresql://bolivia:bolivia@localhost:5432/bolivia_kpis")
        return cls(db_url=db_url)

    def open_spider(self, spider: Spider):
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.cur = self.conn.cursor()
        except Exception as exc:
            logger.warning("DB connection failed – DB pipeline disabled: %s", exc)
            self.conn = None

    def close_spider(self, spider: Spider):
        if self.conn:
            self.conn.commit()
            self.cur.close()
            self.conn.close()

    def process_item(self, item: Any, spider: Spider):
        if self.conn is None:
            return item

        from bolivia_scraper.items import ElectionResultItem

        if isinstance(item, ElectionResultItem):
            try:
                self.cur.execute(
                    """
                    INSERT INTO election_results
                        (year, election_type, party, candidate, votes, percentage, source, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT uq_election_results
                    DO UPDATE SET
                        votes        = EXCLUDED.votes,
                        percentage   = EXCLUDED.percentage,
                        source       = EXCLUDED.source,
                        last_updated = EXCLUDED.last_updated
                    """,
                    (
                        item.get("year"),
                        item.get("election_type"),
                        item.get("party") or "",
                        item.get("candidate") or "",
                        item.get("votes"),
                        item.get("percentage"),
                        item.get("source_url"),
                        datetime.now(timezone.utc),
                    ),
                )
                self.conn.commit()
            except Exception as exc:
                logger.error("DB insert error: %s", exc)
                self.conn.rollback()

        return item
