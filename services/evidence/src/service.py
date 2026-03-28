"""
Evidence business logic — upload, process, map, verify.

v2.1: Real MinIO storage + Azure Document Intelligence parsing.
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import httpx

_ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
_MAX_DOWNLOAD_SIZE = 100 * 1024 * 1024  # 100MB

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from velora_common.logging import get_logger
from .doc_parser import DocumentParser
from .extractors import get_extractor
from .mapping_engine import MappingEngine
from .models import (
    Evidence,
    EvidenceControlMapping,
    EvidenceExtraction,
)
from .schemas import (
    EvidenceControlMappingResponse,
    EvidenceDetailResponse,
    EvidenceExtractionResponse,
    EvidenceFilterParams,
    EvidenceListResponse,
    EvidenceResponse,
    EvidenceUploadRequest,
    EvidenceUploadResponse,
)
from .storage import StorageClient

logger = get_logger(__name__)


def _get_storage() -> StorageClient:
    """Get MinIO storage client."""
    return StorageClient()


def _get_parser() -> DocumentParser:
    """Get Azure Document Intelligence parser."""
    return DocumentParser()


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
        """Create evidence record and return real presigned URL."""
        # Validate mime type against allowlist
        if data.mime_type not in _ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Unsupported file type: {data.mime_type}"
            )

        # Sanitize filename — strip path components and
        # dangerous characters
        safe_name = os.path.basename(data.filename)
        safe_name = re.sub(
            r'[^\w\-. ]', '_', safe_name
        )[:255]
        if not safe_name:
            safe_name = "unnamed_document"

        s3_key = (
            f"evidence/{tenant_id}/{data.vendor_id}"
            f"/{uuid.uuid4()}/{safe_name}"
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

        try:
            storage = _get_storage()
            upload_url = storage.get_presigned_upload_url(
                s3_key
            )
        except Exception:
            logger.warning(
                "minio_presign_failed",
                s3_key=s3_key,
            )
            upload_url = f"minio://{s3_key}"

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

    # -- Process (Real Azure Parsing) --------------------------------

    async def process_evidence(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> Optional[EvidenceDetailResponse]:
        """Parse evidence via Azure Document Intelligence."""
        ev = await self._get_or_none(
            tenant_id, evidence_id
        )
        if ev is None:
            return None

        ev.status = "processing"
        await self._session.flush()

        try:
            parse_result = await self._download_and_parse(ev)
            extractions = self._run_extraction(
                parse_result, ev.document_type,
                tenant_id, evidence_id,
            )
            for ext in extractions:
                self._session.add(ext)

            self._compute_extraction_summary(
                ev, parse_result, extractions,
            )

            if ev.assessment_id and extractions:
                try:
                    await self._auto_map_controls(
                        tenant_id, evidence_id, extractions,
                    )
                except Exception:
                    logger.warning(
                        "auto_mapping_failed",
                        evidence_id=str(evidence_id),
                    )

        except Exception:
            logger.exception(
                "evidence_parse_failed",
                evidence_id=str(evidence_id),
            )
            ev.status = "failed"

        await self._session.flush()

        logger.info(
            "evidence_processed",
            evidence_id=str(evidence_id),
            status=ev.status,
        )
        return await self.get_evidence(
            tenant_id, evidence_id
        )

    async def _download_and_parse(self, ev: Evidence):
        """Download file from MinIO and parse via Azure
        Document Intelligence."""
        storage = _get_storage()
        file_bytes = storage.download_bytes(ev.s3_key)
        if len(file_bytes) > _MAX_DOWNLOAD_SIZE:
            raise ValueError(
                f"File exceeds {_MAX_DOWNLOAD_SIZE} bytes"
            )

        parser = _get_parser()
        parse_result = await parser.parse_document(
            file_bytes,
            content_type=ev.mime_type,
        )
        parser.close()
        return parse_result

    def _run_extraction(
        self,
        parse_result,
        document_type: str,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> List[EvidenceExtraction]:
        """Run typed or generic extractor on parse result."""
        extractor = get_extractor(document_type)
        if extractor:
            return extractor(
                parse_result, tenant_id, evidence_id,
            )
        return self._generic_extractions(
            parse_result, tenant_id, evidence_id,
        )

    @staticmethod
    def _compute_extraction_summary(
        ev: Evidence,
        parse_result,
        extractions: List[EvidenceExtraction],
    ) -> None:
        """Compute and set extraction summary on evidence."""
        confidences = [
            e.confidence for e in extractions
        ]
        avg_conf = (
            sum(confidences) / len(confidences)
            if confidences else 0.0
        )

        ev.status = "parsed"
        ev.parsed_content = {
            "pages": parse_result.total_pages,
            "tables": len(parse_result.tables),
            "kvps": len(parse_result.key_value_pairs),
        }
        ev.extraction_summary = {
            "fields_extracted": len(extractions),
            "avg_confidence": round(avg_conf, 2),
        }
        ev.classification_confidence = round(
            avg_conf, 2
        )

    @staticmethod
    def _generic_extractions(
        parse_result, tenant_id, evidence_id,
    ) -> List[EvidenceExtraction]:
        """Fallback extractor for unknown document types."""
        extractions = []
        for kvp in parse_result.key_value_pairs[:20]:
            extractions.append(EvidenceExtraction(
                tenant_id=tenant_id,
                evidence_id=evidence_id,
                field_name=kvp["key"][:255],
                field_value=kvp["value"][:5000],
                confidence=0.70,
                page_number=None,
            ))
        return extractions

    async def _auto_map_controls(
        self,
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
        extractions: List[EvidenceExtraction],
    ) -> None:
        """Auto-map evidence to framework controls via HTTP."""
        # Get framework_id by querying the framework service
        # for available frameworks (no cross_deps import)
        framework_svc_url = os.environ.get(
            "FRAMEWORK_SERVICE_URL",
            "http://framework-service:8000",
        )
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0)
        ) as client:
            resp = await client.get(
                f"{framework_svc_url}/api/v1"
                f"/internal/frameworks"
            )
            if resp.status_code != 200:
                logger.warning("framework_list_failed")
                return
            frameworks = resp.json()

        if not frameworks or not frameworks.get("items"):
            return

        framework_id = uuid.UUID(
            frameworks["items"][0]["id"]
        )

        engine = MappingEngine(
            tenant_id=tenant_id,
            framework_id=framework_id,
        )
        mappings = await engine.map_evidence(
            evidence_id, extractions,
        )
        for m in mappings:
            self._session.add(m)
        await self._session.flush()

        logger.info(
            "controls_mapped",
            evidence_id=str(evidence_id),
            mappings=len(mappings),
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
