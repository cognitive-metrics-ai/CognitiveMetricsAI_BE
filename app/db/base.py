from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Boolean, DateTime, Column
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Automatically generate __tablename__ from class name (snake_case)."""
        import re
        name = cls.__name__
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when record was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when record was last updated"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Soft deletion / status indicator"
    )
