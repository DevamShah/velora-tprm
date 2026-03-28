"""
Evidence business logic — upload, process, map, verify.

All DB queries run inside the caller-provided async session.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.modules.evidence.models import (
    Evidence,
    EvidenceControlMapping,
    EvidenceExtraction,
)
from app.modules.evidence.schemas import (
    EvidenceControlMappingResponse,
    EvidenceDetailResponse,
    EvidenceExtractionResponse,
    EvidenceFilterParams,
    EvidenceListResponse,
    EvidenceResponse,
    EvidenceUploadRequest,
    EvidenceUploadResponse,
)

logger = get_logger(__name__)


class EvidenceService:
    """Stateless evidence service — receives session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Upload -----------------------------------------------------

    async def upload_evidence(
        self,
        tenant_id: uuid.UUID,
        data: EvidenceUploadRequest,
        uploaded_by: uuid.UUID,
    ) -> EvidenceUploadResponse:
        """Create evidence record and return mock presigned URL."""
        s3_key = (
            f"evidence/{tenant_id}/{data.vendor_id}"
            f"/{uuid.uuid4()}/{data.filename}"
        )
        evidence = Evidence(
            tenant_id=tenant_id,
            vendor_id=data.vendor_id,
            assessment_id=data.assessment_id,
            filename=data.filename,
            file_size=data.file_size,
            mime_type=data.mime_type,
            s3_key=s3_key,
            document_type=data.document_type.value,
            status="uploaded",
            uploaded_by=uploaded_by,
        )
        self._session.add(evidence)
        await self._session.flush()
        logger.info(
            "evidence_uploaded",
            evidence_id=str(evidence.id),
        )
        upload_url = (
            f"https://s3.mock.velora.io/{s3_key}"
            f"?X-Amz-SignedHeaders=host"
        )
        return EvidenceUploadResponse(
            evidence_id=evidence.id,
            upload_url=upload_url,
            s3_key=s3_key,
        )

    # -- Get Detail -------------------------------------------------

    async def get_evidence(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> Optional[EvidenceDetailResponse]:
        """Fetch evidence with extractions and mappings."""
        query = (
            select(Evidence)
            .options(
                selectinload(Evidence.extractions),
                selectinload(Evidence.control_mappings),
            )
            .where(
                Evidence.id == evidence_id,
                Evidence.tenant_id == tenant_id,
                Evidence.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(query)
        ev = result.scalars().first()
        if ev is None:
            return None
        return self._to_detail(ev)

    # -- List -------------------------------------------------------

    async def list_evidence(
        self,
        tenant_id: uuid.UUID,
        filters: EvidenceFilterParams,
    ) -> EvidenceListResponse:
        """List evidence with pagination and filters."""
        base = select(Evidence).where(
            Evidence.tenant_id == tenant_id,
            Evidence.deleted_at.is_(None),
        )
        base = self._apply_filters(base, filters)

        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total = (
            await self._session.execute(count_q)
        ).scalar() or 0

        col = getattr(
            Evidence, filters.sort_by, Evidence.created_at
        )
        if filters.sort_order.value == "desc":
            base = base.order_by(col.desc())
        else:
            base = base.order_by(col.asc())

        offset = (filters.page - 1) * filters.page_size
        base = base.offset(offset).limit(
            filters.page_size
        )
        result = await self._session.execute(base)
        items = result.scalars().all()

        return EvidenceListResponse(
            items=[self._to_response(e) for e in items],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )

    # -- Process (mock AI) ------------------------------------------

    async def process_evidence(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> Optional[EvidenceDetailResponse]:
        """Mock AI parsing — generate sample extractions."""
        ev = await self._get_or_none(
            tenant_id, evidence_id
        )
        if ev is None:
            return None

        ev.status = "processing"
        await self._session.flush()

        extractions = self._generate_mock_extractions(
            tenant_id, evidence_id, ev.document_type
        )
        for ext in extractions:
            self._session.add(ext)

        ev.status = "parsed"
        ev.parsed_content = {
            "pages": 12,
            "sections": ["scope", "controls", "audit"],
        }
        ev.extraction_summary = {
            "fields_extracted": len(extractions),
            "avg_confidence": 0.87,
        }
        ev.classification_confidence = 0.92
        await self._session.flush()

        logger.info(
            "evidence_processed",
            evidence_id=str(evidence_id),
        )
        return await self.get_evidence(
            tenant_id, evidence_id
        )

    # -- Mappings ---------------------------------------------------

    async def get_mappings(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> Optional[List[EvidenceControlMappingResponse]]:
        """Return control mappings for an evidence item."""
        ev = await self._get_or_none(
            tenant_id, evidence_id
        )
        if ev is None:
            return None

        result = await self._session.execute(
            select(EvidenceControlMapping).where(
                EvidenceControlMapping.evidence_id
                == evidence_id,
                EvidenceControlMapping.tenant_id
                == tenant_id,
            )
        )
        mappings = result.scalars().all()
        return [
            self._to_mapping_response(m) for m in mappings
        ]

    async def verify_mapping(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
        mapping_id: uuid.UUID,
        verified: bool,
        verified_by: uuid.UUID,
    ) -> Optional[EvidenceControlMappingResponse]:
        """Verify or reject a control mapping."""
        result = await self._session.execute(
            select(EvidenceControlMapping).where(
                EvidenceControlMapping.id == mapping_id,
                EvidenceControlMapping.evidence_id
                == evidence_id,
                EvidenceControlMapping.tenant_id
                == tenant_id,
            )
        )
        mapping = result.scalars().first()
        if mapping is None:
            return None

        mapping.verified = verified
        mapping.verified_by = (
            verified_by if verified else None
        )
        await self._session.flush()
        logger.info(
            "mapping_verified",
            mapping_id=str(mapping_id),
            verified=verified,
        )
        return self._to_mapping_response(mapping)

    # -- Delete (soft) ----------------------------------------------

    async def delete_evidence(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> bool:
        """Soft-delete evidence. Returns False if not found."""
        ev = await self._get_or_none(
            tenant_id, evidence_id
        )
        if ev is None:
            return False

        ev.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()
        logger.info(
            "evidence_deleted",
            evidence_id=str(evidence_id),
        )
        return True

    # -- Private helpers --------------------------------------------

    async def _get_or_none(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> Optional[Evidence]:
        """Fetch non-deleted evidence or return None."""
        result = await self._session.execute(
            select(Evidence).where(
                Evidence.id == evidence_id,
                Evidence.tenant_id == tenant_id,
                Evidence.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    @staticmethod
    def _apply_filters(query, filters):
        """Apply WHERE clauses for filters."""
        if filters.vendor_id:
            query = query.where(
                Evidence.vendor_id == filters.vendor_id
            )
        if filters.document_type:
            query = query.where(
                Evidence.document_type
                == filters.document_type.value
            )
        if filters.status:
            query = query.where(
                Evidence.status == filters.status.value
            )
        return query

    @staticmethod
    def _generate_mock_extractions(
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
        doc_type: str,
    ) -> List[EvidenceExtraction]:
        """Generate mock extractions based on doc type."""
        field_sets = {
            "soc2": [
                ("audit_period", "2025-01-01 to 2025-12-31", 0.95, 1),
                ("auditor", "Deloitte LLP", 0.98, 1),
                ("opinion_type", "Unqualified", 0.93, 2),
                ("scope", "Cloud hosting infrastructure", 0.88, 3),
            ],
            "iso_cert": [
                ("certificate_number", "IS-2025-78432", 0.97, 1),
                ("standard", "ISO/IEC 27001:2022", 0.99, 1),
                ("valid_until", "2027-03-15", 0.96, 1),
                ("certifying_body", "BSI Group", 0.94, 1),
            ],
            "pen_test": [
                ("test_date", "2025-11-15", 0.96, 1),
                ("tester", "NCC Group", 0.97, 1),
                ("critical_findings", "0", 0.91, 4),
                ("high_findings", "2", 0.89, 5),
            ],
        }
        fields = field_sets.get(doc_type, [
            ("document_title", "Vendor Policy Document", 0.85, 1),
            ("effective_date", "2025-06-01", 0.80, 1),
            ("version", "2.1", 0.90, 1),
        ])
        return [
            EvidenceExtraction(
                tenant_id=tenant_id,
                evidence_id=evidence_id,
                field_name=name,
                field_value=value,
                confidence=conf,
                page_number=page,
            )
            for name, value, conf, page in fields
        ]

    @staticmethod
    def _to_response(ev: Evidence) -> EvidenceResponse:
        """Map Evidence ORM to response schema."""
        return EvidenceResponse(
            id=ev.id,
            tenant_id=ev.tenant_id,
            vendor_id=ev.vendor_id,
            assessment_id=ev.assessment_id,
            filename=ev.filename,
            file_size=ev.file_size,
            mime_type=ev.mime_type,
            s3_key=ev.s3_key,
            document_type=ev.document_type,
            status=ev.status,
            classification_confidence=ev.classification_confidence,
            uploaded_by=ev.uploaded_by,
            created_at=ev.created_at,
            updated_at=ev.updated_at,
        )

    @staticmethod
    def _to_detail(ev: Evidence) -> EvidenceDetailResponse:
        """Map Evidence ORM to detail response."""
        extractions = [
            EvidenceExtractionResponse(
                id=e.id,
                field_name=e.field_name,
                field_value=e.field_value,
                confidence=e.confidence,
                page_number=e.page_number,
                created_at=e.created_at,
            )
            for e in (ev.extractions or [])
        ]
        mappings = [
            EvidenceControlMappingResponse(
                id=m.id,
                evidence_id=m.evidence_id,
                clause_id=m.clause_id,
                coverage_type=m.coverage_type,
                confidence=m.confidence,
                verified=m.verified,
                verified_by=m.verified_by,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in (ev.control_mappings or [])
        ]
        return EvidenceDetailResponse(
            id=ev.id,
            tenant_id=ev.tenant_id,
            vendor_id=ev.vendor_id,
            assessment_id=ev.assessment_id,
            filename=ev.filename,
            file_size=ev.file_size,
            mime_type=ev.mime_type,
            s3_key=ev.s3_key,
            document_type=ev.document_type,
            status=ev.status,
            classification_confidence=ev.classification_confidence,
            uploaded_by=ev.uploaded_by,
            parsed_content=ev.parsed_content,
            extraction_summary=ev.extraction_summary,
            extractions=extractions,
            control_mappings=mappings,
            created_at=ev.created_at,
            updated_at=ev.updated_at,
        )

    @staticmethod
    def _to_mapping_response(
        m: EvidenceControlMapping,
    ) -> EvidenceControlMappingResponse:
        """Map EvidenceControlMapping ORM to response."""
        return EvidenceControlMappingResponse(
            id=m.id,
            evidence_id=m.evidence_id,
            clause_id=m.clause_id,
            coverage_type=m.coverage_type,
            confidence=m.confidence,
            verified=m.verified,
            verified_by=m.verified_by,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
