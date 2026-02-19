"""ETL pipeline base class with extract / transform / load abstraction."""
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ETLPipeline(ABC):
    """Base class for all ETL pipelines.

    Sub-classes must implement extract(), transform(), and load().
    run() coordinates execution and provides hash-based change detection
    so that identical source data is not re-processed.
    """

    name: str = "base"
    hash_store_dir: Path = Path("data/processed/.hashes")

    def __init__(self):
        self.hash_store_dir.mkdir(parents=True, exist_ok=True)
        self._hash_file = self.hash_store_dir / f"{self.name}.sha256"

    # ── Abstract methods ──────────────────────────────────────────────────────

    @abstractmethod
    def extract(self) -> Any:
        """Fetch / read raw source data. Return raw data object."""

    @abstractmethod
    def transform(self, raw: Any) -> Any:
        """Clean and reshape raw data. Return transformed data."""

    @abstractmethod
    def load(self, data: Any) -> None:
        """Persist transformed data to the target store."""

    # ── Concrete helpers ──────────────────────────────────────────────────────

    def run(self) -> bool:
        """Execute the full ETL pipeline.

        Returns True if data was loaded (changed), False if skipped.
        """
        logger.info("[%s] Starting extract phase", self.name)
        raw = self.extract()

        raw_hash = self._compute_hash(raw)
        if self._hash_unchanged(raw_hash):
            logger.info("[%s] Source data unchanged – skipping transform/load", self.name)
            return False

        logger.info("[%s] Starting transform phase", self.name)
        data = self.transform(raw)

        logger.info("[%s] Starting load phase", self.name)
        self.load(data)

        self._save_hash(raw_hash)
        logger.info("[%s] Pipeline complete", self.name)
        return True

    # ── Hash helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(data: Any) -> str:
        if isinstance(data, bytes):
            content = data
        elif isinstance(data, str):
            content = data.encode()
        else:
            content = json.dumps(data, sort_keys=True, default=str).encode()
        return hashlib.sha256(content).hexdigest()

    def _hash_unchanged(self, new_hash: str) -> bool:
        if not self._hash_file.exists():
            return False
        return self._hash_file.read_text().strip() == new_hash

    def _save_hash(self, hash_value: str) -> None:
        self._hash_file.write_text(hash_value)
