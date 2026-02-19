from datetime import datetime
from sqlalchemy import Column, DateTime, String, func
from database import Base


class TimestampMixin:
    """Adds audit timestamp columns to any model."""

    created_at: datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    source: str = Column(String(512), nullable=True)
    last_updated: datetime = Column(DateTime(timezone=True), nullable=True)


__all__ = ["Base", "TimestampMixin"]
