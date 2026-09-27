"""
Repository for the Analysis entity.

All database access for the `analyses` table is centralised here.
Service and agent code must go through this class — never use the
session directly outside this module.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis, AnalysisStatus
from app.schemas.analysis import AnalysisCreate


class AnalysisRepository:
    """Async data-access layer for Analysis records."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Write ─────────────────────────────────────────────────────────────────

    async def create_analysis(self, payload: AnalysisCreate) -> Analysis:
        """
        Persist a new Analysis row with status ``pending`` and return it.

        Parameters
        ----------
        payload:
            Validated ``AnalysisCreate`` schema carrying the request text.

        Returns
        -------
        Analysis
            The newly created ORM instance (id and timestamps populated).
        """
        record = Analysis(
            request_text=payload.request_text,
            status=AnalysisStatus.pending,
        )
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_analysis(self, analysis_id: uuid.UUID) -> Analysis | None:
        """
        Fetch a single Analysis by primary key.

        Parameters
        ----------
        analysis_id:
            The UUID of the record to retrieve.

        Returns
        -------
        Analysis | None
            The ORM instance, or ``None`` if no matching row exists.
        """
        result = await self._session.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    # ── Update ────────────────────────────────────────────────────────────────

    async def update_status(
        self,
        analysis_id: uuid.UUID,
        new_status: AnalysisStatus,
    ) -> Analysis | None:
        """
        Transition an Analysis to a new lifecycle status.

        Parameters
        ----------
        analysis_id:
            The UUID of the record to update.
        new_status:
            The target ``AnalysisStatus`` value.

        Returns
        -------
        Analysis | None
            The updated ORM instance, or ``None`` if the record was not found.
        """
        record = await self.get_analysis(analysis_id)
        if record is None:
            return None

        record.status = new_status
        await self._session.commit()
        await self._session.refresh(record)
        return record
