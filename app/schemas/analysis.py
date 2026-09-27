"""
Pydantic v2 schemas for the Analysis domain.

These schemas are the contract between the HTTP layer and the service layer.
They are intentionally separate from the ORM model so that the database
shape and the API shape can evolve independently.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.analysis import AnalysisStatus


# ── Request ───────────────────────────────────────────────────────────────────

class AnalysisCreate(BaseModel):
    """Payload required to create a new Analysis."""

    request_text: str = Field(
        ...,
        min_length=1,
        description="Description of the proposed code change to be analysed.",
    )


# ── Responses ─────────────────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    """Full representation of an Analysis record returned to the caller."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_text: str
    status: AnalysisStatus
    created_at: datetime
    updated_at: datetime


class AnalysisStatusResponse(BaseModel):
    """Lightweight projection used when only the lifecycle state is needed."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: AnalysisStatus
    updated_at: datetime
