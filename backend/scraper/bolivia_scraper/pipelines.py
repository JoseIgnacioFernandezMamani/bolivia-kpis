"""Item pipelines for Crawlee-based scraper."""
import hashlib
import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import redis as redis_lib
import psycopg2

from bolivia_scraper import settings
from bolivia_scraper.items import ElectionResultItem

logger = logging.getLogger(__name__)


class DropItem(Exception):
    """Raised by a pipeline to signal the item should not be processed further."""


def _item_hash(item: Any) -> str:
    """Return SHA-256 hex digest of a deterministic JSON representation."""
    d = asdict(item) if hasattr(item, "__dataclass_fields__") else dict(item)
    d.pop("scraped_at", None)
    canonical = json.dumps(d, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


class HashCheckPipeline:
    """Drop items whose content hash has not changed since the last run."""

    def __init__(self) -> None:
        self._redis: redis_lib.Redis | None = None
        try:
            self._redis = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
            self._redis.ping()
        except Exception as exc:
            logger.warning("Redis unavailable – hash check disabled: %s", exc)
            self._redis = None

    def process(self, spider_name: str, item: Any) -> Any:
        if self._redis is None:
            return item

        key = f"hash:{spider_name}:{_item_hash(item)}"
        if self._redis.get(key):
            raise DropItem(f"Unchanged item – skipping")

        self._redis.set(key, "1", ex=settings.HASH_TTL_SECONDS)
        return item


class JsonExportPipeline:
    """Append each item to a JSONL file under data/raw/<spider_name>.jsonl"""

    def __init__(self) -> None:
        self._raw_dir = Path(settings.DATA_RAW_DIR)
        self._raw_dir.mkdir(parents=True, exist_ok=True)
        self._handles: dict[str, Any] = {}

    def process(self, spider_name: str, item: Any) -> Any:
        if spider_name not in self._handles:
            path = self._raw_dir / f"{spider_name}.jsonl"
            self._handles[spider_name] = open(path, "a", encoding="utf-8")
        d = asdict(item) if hasattr(item, "__dataclass_fields__") else dict(item)
        self._handles[spider_name].write(json.dumps(d, default=str) + "\n")
        return item

    def close(self) -> None:
        for fh in self._handles.values():
            fh.close()
        self._handles.clear()


class DatabasePipeline:
    """Upsert election results into PostgreSQL."""

    def __init__(self) -> None:
        self._conn: psycopg2.extensions.connection | None = None
        self._cur: psycopg2.extensions.cursor | None = None
        try:
            self._conn = psycopg2.connect(settings.DATABASE_SYNC_URL)
            self._cur = self._conn.cursor()
        except Exception as exc:
            logger.warning("DB connection failed – DB pipeline disabled: %s", exc)
            self._conn = None

    def process(self, spider_name: str, item: Any) -> Any:
        if self._conn is None:
            return item

        if isinstance(item, ElectionResultItem):
            try:
                self._cur.execute(
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
                        item.year,
                        item.election_type,
                        item.party or "",
                        item.candidate or "",
                        item.votes,
                        item.percentage,
                        item.source_url,
                        datetime.now(timezone.utc),
                    ),
                )
                self._conn.commit()
            except Exception as exc:
                logger.error("DB insert error: %s", exc)
                self._conn.rollback()

        return item

    def close(self) -> None:
        if self._conn:
            self._conn.commit()
            if self._cur:
                self._cur.close()
            self._conn.close()


def run_pipelines(spider_name: str, items: list[Any]) -> int:
    """Run all pipelines over a list of items. Returns count of persisted items."""
    hash_pipe = HashCheckPipeline()
    json_pipe = JsonExportPipeline()
    db_pipe = DatabasePipeline()

    saved = 0
    for item in items:
        try:
            item = hash_pipe.process(spider_name, item)
            item = json_pipe.process(spider_name, item)
            item = db_pipe.process(spider_name, item)
            saved += 1
        except DropItem:
            pass
        except Exception as exc:
            logger.error("Pipeline error for %s: %s", spider_name, exc)

    json_pipe.close()
    db_pipe.close()
    return saved
