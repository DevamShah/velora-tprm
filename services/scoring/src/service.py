"""
Scoring engine business logic — model CRUD, score calculation,
history tracking, and portfolio summary.

Tenant-scoped. Calculation logic delegated to engine.py.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.logging import get_logger
from . import engine
from .models import (
    ScoreHistory, ScoringModel, VendorScore,
)
from .schemas import (
    BulkCalculateResponse, PortfolioSummary,
    ScoreBreakdown, ScoreHistoryItem,
    ScoreHistoryResponse, ScoringModelCreate,
    ScoringModelResponse, ScoringModelUpdate,
    TierDistribution,
)
from .cross_deps.vendor_models import Vendor  # TODO: Replace with API call in Phase 2

logger = get_logger(__name__)


class ScoringService:
    """Stateless scoring service — receives a session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_models(
        self, tenant_id: uuid.UUID
    ) -> List[ScoringModelResponse]:
        """List scoring models for a tenant."""
        query = (
            select(ScoringModel)
            .where(ScoringModel.tenant_id == tenant_id)
            .order_by(ScoringModel.created_at.desc())
        )
        result = await self._session.execute(query)
        return [
            self._to_model_response(m)
            for m in result.scalars().all()
        ]

    async def create_model(
        self,
        tenant_id: uuid.UUID,
        data: ScoringModelCreate,
    ) -> ScoringModelResponse:
        """Create a new scoring model."""
        config = {
            "dimensions": [
                d.model_dump() for d in data.dimensions
            ]
        }
        model = ScoringModel(
            tenant_id=tenant_id, name=data.name,
            description=data.description,
            method=data.method.value,
            is_default=data.is_default, config=config,
            inherent_risk_factors=data.inherent_risk_factors,
            risk_thresholds=data.risk_thresholds,
        )
        if data.is_default:
            await self._clear_default(tenant_id)
        self._session.add(model)
        await self._session.flush()
        logger.info("scoring_model_created", model_id=str(model.id))
        return self._to_model_response(model)

    async def update_model(
        self,
        tenant_id: uuid.UUID,
        model_id: uuid.UUID,
        data: ScoringModelUpdate,
    ) -> Optional[ScoringModelResponse]:
        """Update an existing scoring model."""
        model = await self._get_model_or_none(tenant_id, model_id)
        if model is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        dims = update_data.pop("dimensions", None)
        if dims is not None:
            model.config = {
                "dimensions": [
                    d.model_dump() for d in data.dimensions
                ]
            }
        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(model, field, value)
        if data.is_default:
            await self._clear_default(tenant_id, exclude=model_id)
        await self._session.flush()
        return self._to_model_response(model)

    async def calculate_score(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
        scoring_model_id: Optional[uuid.UUID] = None,
    ) -> Optional[ScoreBreakdown]:
        """Run scoring algorithm for a vendor."""
        vendor = await self._get_vendor(
            tenant_id, vendor_id
        )
        if vendor is None:
            return None
        model = await self._resolve_model(
            tenant_id, scoring_model_id
        )
        if model is None:
            raise ValueError(
                "No scoring model found for tenant"
            )
        return await self._execute_scoring(
            tenant_id, vendor, model
        )

    async def bulk_calculate(
        self,
        tenant_id: uuid.UUID,
        vendor_ids: List[uuid.UUID],
        scoring_model_id: Optional[uuid.UUID] = None,
    ) -> BulkCalculateResponse:
        """Calculate scores for multiple vendors."""
        results: List[ScoreBreakdown] = []
        errors: List[Dict[str, str]] = []
        for vid in vendor_ids:
            try:
                r = await self.calculate_score(
                    tenant_id, vid, scoring_model_id
                )
                if r:
                    results.append(r)
                else:
                    errors.append({
                        "vendor_id": str(vid),
                        "error": "Vendor not found",
                    })
            except Exception as exc:
                errors.append({
                    "vendor_id": str(vid),
                    "error": str(exc),
                })
        return BulkCalculateResponse(
            calculated=len(results),
            failed=len(errors),
            results=results,
            errors=errors,
        )

    async def get_vendor_score(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> Optional[ScoreBreakdown]:
        """Get the most recent score for a vendor."""
        query = (
            select(VendorScore)
            .where(
                VendorScore.tenant_id == tenant_id,
                VendorScore.vendor_id == vendor_id,
            )
            .order_by(VendorScore.calculated_at.desc())
            .limit(1)
        )
        result = await self._session.execute(query)
        score = result.scalars().first()
        if score is None:
            return None
        thresholds = await self._get_thresholds(
            tenant_id, score.scoring_model_id
        )
        return self._score_to_breakdown(
            score, thresholds
        )

    async def get_score_history(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> ScoreHistoryResponse:
        """Get historical scores for trend analysis."""
        query = (
            select(ScoreHistory)
            .where(
                ScoreHistory.tenant_id == tenant_id,
                ScoreHistory.vendor_id == vendor_id,
            )
            .order_by(ScoreHistory.recorded_at.desc())
        )
        result = await self._session.execute(query)
        items = [
            ScoreHistoryItem(
                id=r.id,
                overall_score=r.overall_score,
                dimension_scores=r.dimension_scores,
                recorded_at=r.recorded_at,
            )
            for r in result.scalars().all()
        ]
        return ScoreHistoryResponse(
            vendor_id=vendor_id,
            items=items,
            total=len(items),
        )

    async def get_portfolio_summary(
        self, tenant_id: uuid.UUID
    ) -> PortfolioSummary:
        """Aggregate scoring summary across portfolio."""
        total_vendors = await self._count_vendors(
            tenant_id
        )
        latest = await self._latest_scores(tenant_id)
        if not latest:
            return PortfolioSummary(
                total_vendors=total_vendors
            )

        avg = round(
            sum(s.overall_score for s in latest)
            / len(latest),
            2,
        )
        tier_dist = TierDistribution()
        risk_counts: Dict[str, int] = {}
        for s in latest:
            level = engine.classify_risk(s.overall_score, None)
            risk_counts[level] = (
                risk_counts.get(level, 0) + 1
            )
            setattr(
                tier_dist,
                level,
                getattr(tier_dist, level, 0) + 1,
            )
        return PortfolioSummary(
            total_vendors=total_vendors,
            scored_vendors=len(latest),
            average_score=avg,
            tier_distribution=tier_dist,
            risk_level_counts=risk_counts,
        )

    async def _execute_scoring(
        self, tenant_id: uuid.UUID,
        vendor: Vendor, model: ScoringModel,
    ) -> ScoreBreakdown:
        """Core scoring logic — calculate and persist."""
        dims = engine.extract_dimensions(model)
        dim_scores = engine.calculate_dimensions(vendor, dims)
        overall = engine.aggregate_score(model.method, dim_scores, dims)
        now = datetime.now(timezone.utc)
        inherent = engine.calculate_inherent(vendor, model)
        residual, external = max(0.0, overall), vendor.external_rating_score
        score = VendorScore(
            tenant_id=tenant_id, vendor_id=vendor.id,
            scoring_model_id=model.id, overall_score=overall,
            dimension_scores=dim_scores, inherent_score=inherent,
            residual_score=residual, external_score=external,
            input_snapshot=engine.build_snapshot(vendor), calculated_at=now,
        )
        self._session.add(score)
        self._session.add(ScoreHistory(
            tenant_id=tenant_id, vendor_id=vendor.id,
            overall_score=overall, dimension_scores=dim_scores,
            recorded_at=now,
        ))
        vendor.inherent_risk_score = inherent
        vendor.residual_risk_score = residual
        await self._session.flush()
        return ScoreBreakdown(
            id=score.id, vendor_id=vendor.id,
            scoring_model_id=model.id, overall_score=overall,
            dimension_scores=dim_scores, inherent_score=inherent,
            residual_score=residual, external_score=external,
            risk_level=engine.classify_risk(overall, model.risk_thresholds),
            calculated_at=now, created_at=score.created_at,
        )

    async def _get_model_or_none(
        self, tenant_id: uuid.UUID, model_id: uuid.UUID,
    ) -> Optional[ScoringModel]:
        r = await self._session.execute(select(ScoringModel).where(
            ScoringModel.id == model_id, ScoringModel.tenant_id == tenant_id))
        return r.scalars().first()

    async def _resolve_model(
        self, tenant_id: uuid.UUID, model_id: Optional[uuid.UUID],
    ) -> Optional[ScoringModel]:
        if model_id:
            return await self._get_model_or_none(tenant_id, model_id)
        r = await self._session.execute(select(ScoringModel).where(
            ScoringModel.tenant_id == tenant_id, ScoringModel.is_default.is_(True)))
        return r.scalars().first()

    async def _get_vendor(
        self, tenant_id: uuid.UUID, vendor_id: uuid.UUID,
    ) -> Optional[Vendor]:
        r = await self._session.execute(select(Vendor).where(
            Vendor.id == vendor_id, Vendor.tenant_id == tenant_id,
            Vendor.deleted_at.is_(None)))
        return r.scalars().first()

    async def _clear_default(
        self, tenant_id: uuid.UUID, exclude: Optional[uuid.UUID] = None,
    ) -> None:
        q = select(ScoringModel).where(
            ScoringModel.tenant_id == tenant_id, ScoringModel.is_default.is_(True))
        if exclude:
            q = q.where(ScoringModel.id != exclude)
        for m in (await self._session.execute(q)).scalars().all():
            m.is_default = False

    async def _get_thresholds(
        self, tenant_id: uuid.UUID, model_id: Optional[uuid.UUID],
    ) -> Optional[Dict]:
        if not model_id:
            return None
        m = await self._get_model_or_none(tenant_id, model_id)
        return m.risk_thresholds if m else None

    async def _count_vendors(self, tenant_id: uuid.UUID) -> int:
        r = await self._session.execute(select(func.count()).where(
            Vendor.tenant_id == tenant_id, Vendor.deleted_at.is_(None)))
        return r.scalar() or 0

    async def _latest_scores(self, tenant_id: uuid.UUID) -> list:
        q = (select(VendorScore).where(VendorScore.tenant_id == tenant_id)
             .distinct(VendorScore.vendor_id)
             .order_by(VendorScore.vendor_id, VendorScore.calculated_at.desc()))
        return list((await self._session.execute(q)).scalars().all())

    @staticmethod
    def _score_to_breakdown(
        score: VendorScore, thresholds: Optional[Dict],
    ) -> ScoreBreakdown:
        return ScoreBreakdown(
            id=score.id, vendor_id=score.vendor_id,
            scoring_model_id=score.scoring_model_id,
            overall_score=score.overall_score,
            dimension_scores=score.dimension_scores,
            inherent_score=score.inherent_score,
            residual_score=score.residual_score,
            external_score=score.external_score,
            risk_level=engine.classify_risk(score.overall_score, thresholds),
            calculated_at=score.calculated_at,
            created_at=score.created_at,
        )

    @staticmethod
    def _to_model_response(model: ScoringModel) -> ScoringModelResponse:
        return ScoringModelResponse(
            id=model.id, tenant_id=model.tenant_id,
            name=model.name, description=model.description,
            method=model.method, is_default=model.is_default,
            config=model.config,
            inherent_risk_factors=model.inherent_risk_factors,
            risk_thresholds=model.risk_thresholds,
            created_at=model.created_at, updated_at=model.updated_at,
        )
