from sqlalchemy import Column, DateTime, String, func
from database import Base


class TimestampMixin:
    """Adds audit timestamp columns to any model."""

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    source = Column(String(512), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)


__all__ = ["Base", "TimestampMixin"]

