"""
Reports business logic — dashboards, report generation, templates.

All DB queries run inside the caller-provided async session.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.modules.monitoring.models import Alert
from app.modules.reports.models import (
    DashboardConfig,
    GeneratedReport,
    ReportTemplate,
)
from app.modules.reports.schemas import (
    AlertsByPriority,
    AssessmentsByStatus,
    DashboardConfigResponse,
    DashboardConfigUpdate,
    ExecutiveDashboardData,
    FindingsBySeverity,
    RecentAlert,
    ReportListResponse,
    ReportResponse,
    ReportTemplateResponse,
    TopRiskVendor,
    VendorsByTier,
)
from app.modules.vendors.models import Vendor

logger = get_logger(__name__)


class ReportsService:
    """Stateless reports service — receives session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Executive Dashboard ----------------------------------------

    async def get_executive_dashboard(
        self,
        tenant_id: uuid.UUID,
    ) -> ExecutiveDashboardData:
        """Aggregate cross-module data for executive view."""
        vendors_data = await self._get_vendor_stats(
            tenant_id
        )
        assessments_data = await self._get_assessment_stats(
            tenant_id
        )
        findings_data = await self._get_finding_stats(
            tenant_id
        )
        alerts_data = await self._get_alert_stats(
            tenant_id
        )
        avg_score = await self._get_avg_risk_score(
            tenant_id
        )
        recent = await self._get_recent_alerts(tenant_id)
        top_risk = await self._get_top_risk_vendors(
            tenant_id
        )

        return ExecutiveDashboardData(
            **vendors_data,
            **assessments_data,
            **findings_data,
            **alerts_data,
            avg_risk_score=avg_score,
            recent_alerts=recent,
            top_risk_vendors=top_risk,
        )

    # -- Report Generation ------------------------------------------

    async def generate_report(
        self,
        tenant_id: uuid.UUID,
        template_id: Optional[uuid.UUID],
        title: str,
        fmt: str,
        generated_by: uuid.UUID,
    ) -> ReportResponse:
        """Create a report generation record."""
        report = GeneratedReport(
            tenant_id=tenant_id,
            template_id=template_id,
            title=title,
            format=fmt,
            status="pending",
            generated_by=generated_by,
        )
        self._session.add(report)
        await self._session.flush()
        logger.info(
            "report_generated", report_id=str(report.id)
        )
        return self._to_report_response(report)

    # -- List Reports -----------------------------------------------

    async def list_reports(
        self,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> ReportListResponse:
        """List generated reports with pagination."""
        base = select(GeneratedReport).where(
            GeneratedReport.tenant_id == tenant_id
        )
        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total = (
            await self._session.execute(count_q)
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await self._session.execute(
            base.order_by(
                GeneratedReport.created_at.desc()
            )
            .offset(offset)
            .limit(page_size)
        )
        reports = result.scalars().all()

        return ReportListResponse(
            items=[
                self._to_report_response(r)
                for r in reports
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    # -- Get Report -------------------------------------------------

    async def get_report(
        self,
        tenant_id: uuid.UUID,
        report_id: uuid.UUID,
    ) -> Optional[ReportResponse]:
        """Fetch a single generated report."""
        result = await self._session.execute(
            select(GeneratedReport).where(
                GeneratedReport.id == report_id,
                GeneratedReport.tenant_id == tenant_id,
            )
        )
        report = result.scalars().first()
        if report is None:
            return None
        return self._to_report_response(report)

    # -- Templates --------------------------------------------------

    async def list_templates(
        self,
        tenant_id: uuid.UUID,
    ) -> List[ReportTemplateResponse]:
        """List all report templates for tenant."""
        result = await self._session.execute(
            select(ReportTemplate).where(
                ReportTemplate.tenant_id == tenant_id
            )
        )
        templates = result.scalars().all()
        return [
            self._to_template_response(t)
            for t in templates
        ]

    # -- Dashboard Config -------------------------------------------

    async def get_dashboard_config(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[DashboardConfigResponse]:
        """Fetch user's dashboard configuration."""
        result = await self._session.execute(
            select(DashboardConfig).where(
                DashboardConfig.tenant_id == tenant_id,
                DashboardConfig.user_id == user_id,
            )
        )
        config = result.scalars().first()
        if config is None:
            return None
        return self._to_config_response(config)

    async def update_dashboard_config(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        data: DashboardConfigUpdate,
    ) -> DashboardConfigResponse:
        """Create or update dashboard configuration."""
        result = await self._session.execute(
            select(DashboardConfig).where(
                DashboardConfig.tenant_id == tenant_id,
                DashboardConfig.user_id == user_id,
            )
        )
        config = result.scalars().first()

        if config is None:
            config = DashboardConfig(
                tenant_id=tenant_id,
                user_id=user_id,
                dashboard_type=data.dashboard_type
                or "executive",
                widget_layout=data.widget_layout,
            )
            self._session.add(config)
        else:
            update_data = data.model_dump(
                exclude_unset=True
            )
            for field, value in update_data.items():
                setattr(config, field, value)

        await self._session.flush()
        return self._to_config_response(config)

    # -- Private: vendor stats --------------------------------------

    async def _get_vendor_stats(
        self, tenant_id: uuid.UUID
    ) -> dict:
        """Count vendors total and by tier."""
        result = await self._session.execute(
            select(
                Vendor.tier, func.count(Vendor.id)
            )
            .where(
                Vendor.tenant_id == tenant_id,
                Vendor.deleted_at.is_(None),
            )
            .group_by(Vendor.tier)
        )
        rows = result.all()
        total = sum(r[1] for r in rows)
        tier_map = {r[0]: r[1] for r in rows}

        return {
            "total_vendors": total,
            "vendors_by_tier": VendorsByTier(
                critical=tier_map.get("critical", 0),
                high=tier_map.get("high", 0),
                medium=tier_map.get("medium", 0),
                low=tier_map.get("low", 0),
                unclassified=tier_map.get(
                    "unclassified", 0
                ),
            ),
        }

    # -- Private: assessment stats ----------------------------------

    async def _get_assessment_stats(
        self, tenant_id: uuid.UUID
    ) -> dict:
        """Count assessments total and by status."""
        from app.modules.assessments.models import (
            Assessment,
        )

        result = await self._session.execute(
            select(
                Assessment.status,
                func.count(Assessment.id),
            )
            .where(Assessment.tenant_id == tenant_id)
            .group_by(Assessment.status)
        )
        rows = result.all()
        total = sum(r[1] for r in rows)
        status_map = {r[0]: r[1] for r in rows}

        return {
            "total_assessments": total,
            "assessments_by_status": AssessmentsByStatus(
                draft=status_map.get("draft", 0),
                in_progress=status_map.get(
                    "in_progress", 0
                ),
                submitted=status_map.get("submitted", 0),
                completed=status_map.get("completed", 0),
                overdue=status_map.get("overdue", 0),
            ),
        }

    # -- Private: finding stats -------------------------------------

    async def _get_finding_stats(
        self, tenant_id: uuid.UUID
    ) -> dict:
        """Count open findings total and by severity."""
        from app.modules.findings.models import Finding

        result = await self._session.execute(
            select(
                Finding.severity,
                func.count(Finding.id),
            )
            .where(
                Finding.tenant_id == tenant_id,
                Finding.status.in_(
                    [
                        "open",
                        "remediation_in_progress",
                        "submitted_for_verification",
                    ]
                ),
            )
            .group_by(Finding.severity)
        )
        rows = result.all()
        total = sum(r[1] for r in rows)
        sev_map = {r[0]: r[1] for r in rows}

        return {
            "open_findings": total,
            "findings_by_severity": FindingsBySeverity(
                critical=sev_map.get("critical", 0),
                high=sev_map.get("high", 0),
                medium=sev_map.get("medium", 0),
                low=sev_map.get("low", 0),
                info=sev_map.get("info", 0),
            ),
        }

    # -- Private: alert stats ---------------------------------------

    async def _get_alert_stats(
        self, tenant_id: uuid.UUID
    ) -> dict:
        """Count active alerts total and by priority."""
        result = await self._session.execute(
            select(
                Alert.priority, func.count(Alert.id)
            )
            .where(
                Alert.tenant_id == tenant_id,
                Alert.status.in_(
                    ["new", "acknowledged", "investigating"]
                ),
            )
            .group_by(Alert.priority)
        )
        rows = result.all()
        total = sum(r[1] for r in rows)
        pri_map = {r[0]: r[1] for r in rows}

        return {
            "active_alerts": total,
            "alerts_by_priority": AlertsByPriority(
                p0=pri_map.get("p0", 0),
                p1=pri_map.get("p1", 0),
                p2=pri_map.get("p2", 0),
                p3=pri_map.get("p3", 0),
                p4=pri_map.get("p4", 0),
            ),
        }

    # -- Private: averages ------------------------------------------

    async def _get_avg_risk_score(
        self, tenant_id: uuid.UUID
    ) -> Optional[float]:
        """Average inherent risk score across vendors."""
        result = await self._session.execute(
            select(
                func.avg(Vendor.inherent_risk_score)
            ).where(
                Vendor.tenant_id == tenant_id,
                Vendor.deleted_at.is_(None),
                Vendor.inherent_risk_score.isnot(None),
            )
        )
        val = result.scalar()
        return round(val, 2) if val else None

    # -- Private: recent alerts -------------------------------------

    async def _get_recent_alerts(
        self, tenant_id: uuid.UUID
    ) -> List[RecentAlert]:
        """Fetch 5 most recent alerts."""
        result = await self._session.execute(
            select(Alert)
            .where(Alert.tenant_id == tenant_id)
            .order_by(Alert.created_at.desc())
            .limit(5)
        )
        alerts = result.scalars().all()
        return [
            RecentAlert(
                id=a.id,
                title=a.title,
                priority=a.priority,
                vendor_id=a.vendor_id,
                created_at=a.created_at,
            )
            for a in alerts
        ]

    # -- Private: top risk vendors ----------------------------------

    async def _get_top_risk_vendors(
        self, tenant_id: uuid.UUID
    ) -> List[TopRiskVendor]:
        """Fetch top 5 vendors by inherent risk score."""
        result = await self._session.execute(
            select(Vendor)
            .where(
                Vendor.tenant_id == tenant_id,
                Vendor.deleted_at.is_(None),
                Vendor.inherent_risk_score.isnot(None),
            )
            .order_by(
                Vendor.inherent_risk_score.desc()
            )
            .limit(5)
        )
        vendors = result.scalars().all()
        return [
            TopRiskVendor(
                id=v.id,
                name=v.name,
                tier=v.tier,
                inherent_risk_score=v.inherent_risk_score,
                open_findings=0,
            )
            for v in vendors
        ]

    # -- Mappers ----------------------------------------------------

    @staticmethod
    def _to_report_response(
        report: GeneratedReport,
    ) -> ReportResponse:
        """Map GeneratedReport ORM to response schema."""
        return ReportResponse(
            id=report.id,
            tenant_id=report.tenant_id,
            template_id=report.template_id,
            title=report.title,
            format=report.format,
            status=report.status,
            s3_key=report.s3_key,
            generated_by=report.generated_by,
            created_at=report.created_at,
            updated_at=report.updated_at,
        )

    @staticmethod
    def _to_template_response(
        template: ReportTemplate,
    ) -> ReportTemplateResponse:
        """Map ReportTemplate ORM to response schema."""
        return ReportTemplateResponse(
            id=template.id,
            tenant_id=template.tenant_id,
            name=template.name,
            description=template.description,
            template_type=template.template_type,
            sections=template.sections,
            is_system=template.is_system,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    @staticmethod
    def _to_config_response(
        config: DashboardConfig,
    ) -> DashboardConfigResponse:
        """Map DashboardConfig ORM to response schema."""
        return DashboardConfigResponse(
            id=config.id,
            tenant_id=config.tenant_id,
            user_id=config.user_id,
            dashboard_type=config.dashboard_type,
            widget_layout=config.widget_layout,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
