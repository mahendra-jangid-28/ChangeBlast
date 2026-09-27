"""
ORM model for the `analyses` table.

Represents one requested change analysis submitted by a caller.
Uses SQLAlchemy 2.0 mapped-column style throughout.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnalysisStatus(str, enum.Enum):
    """Valid lifecycle states for an Analysis record."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Analysis(Base):
    __tablename__ = "analyses"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Payload ───────────────────────────────────────────────────────────────
    request_text: Mapped[str] = mapped_column(Text, nullable=False)

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, name="analysisstatus"),
        nullable=False,
        default=AnalysisStatus.pending,
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Analysis id={self.id} status={self.status}>"
