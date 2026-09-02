"""
Vendor business logic — CRUD, bulk import, tier calculation, contacts.

All DB queries run inside the caller-provided async session.
PII fields are encrypted/decrypted via FieldEncryptor.
"""

from __future__ import annotations

import csv
import io
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import FieldEncryptor
from app.modules.vendors.models import (
    Vendor,
    VendorContact,
)
from app.modules.vendors.schemas import (
    BulkImportError,
    BulkImportResult,
    VendorContactCreate,
    VendorContactResponse,
    VendorContactUpdate,
    VendorCreate,
    VendorDetailResponse,
    VendorEnrichmentResponse,
    VendorFilterParams,
    VendorListResponse,
    VendorResponse,
    VendorUpdate,
)

logger = get_logger(__name__)


class VendorService:
    """Stateless vendor service — receives a session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()
        self._encryptor = FieldEncryptor(
            self._settings.ENCRYPTION_KEY
        )

    # ── Create ─────────────────────────────────────────────

    async def create_vendor(
        self,
        tenant_id: uuid.UUID,
        data: VendorCreate,
    ) -> VendorResponse:
        """Create a new vendor record."""
        vendor = Vendor(
            tenant_id=tenant_id,
            name=data.name,
            domain=data.domain,
            description=data.description,
            status=(data.status or "discovered").value
            if data.status
            else "discovered",
            tier=(data.tier or "unclassified").value
            if data.tier
            else "unclassified",
            industry=data.industry,
            country=data.country,
            employee_count=data.employee_count,
            annual_revenue=data.annual_revenue,
            data_classification=data.data_classification.value
            if data.data_classification
            else None,
            business_criticality=data.business_criticality.value
            if data.business_criticality
            else None,
            contract_start_date=data.contract_start_date,
            contract_end_date=data.contract_end_date,
            contract_value=data.contract_value,
            primary_contact_name=data.primary_contact_name,
            tags=data.tags or [],
            notes=data.notes,
            inherent_risk_score=data.inherent_risk_score,
            residual_risk_score=data.residual_risk_score,
        )
        self._set_encrypted_email(vendor, data.primary_contact_email)
        self._session.add(vendor)
        await self._session.flush()
        logger.info("vendor_created", vendor_id=str(vendor.id))
        return self._to_response(vendor)

    # ── List ───────────────────────────────────────────────

    async def list_vendors(
        self,
        tenant_id: uuid.UUID,
        filters: VendorFilterParams,
    ) -> VendorListResponse:
        """List vendors with pagination, filtering, sorting, search."""
        base = select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.deleted_at.is_(None),
        )
        base = self._apply_filters(base, filters)
        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total_result = await self._session.execute(count_q)
        total = total_result.scalar() or 0

        base = self._apply_sorting(base, filters)
        offset = (filters.page - 1) * filters.page_size
        base = base.offset(offset).limit(filters.page_size)

        result = await self._session.execute(base)
        vendors = result.scalars().all()

        return VendorListResponse(
            items=[self._to_response(v) for v in vendors],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )

    # ── Get Detail ─────────────────────────────────────────

    async def get_vendor(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> VendorDetailResponse | None:
        """Fetch a vendor with contacts and enrichment data."""
        query = (
            select(Vendor)
            .options(
                selectinload(Vendor.contacts),
                selectinload(Vendor.enrichments),
            )
            .where(
                Vendor.id == vendor_id,
                Vendor.tenant_id == tenant_id,
                Vendor.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(query)
        vendor = result.scalars().first()
        if vendor is None:
            return None
        return self._to_detail_response(vendor)

    # ── Update ─────────────────────────────────────────────

    async def update_vendor(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
        data: VendorUpdate,
    ) -> VendorResponse | None:
        """Update an existing vendor. Returns None if not found."""
        vendor = await self._get_vendor_or_none(
            tenant_id, vendor_id
        )
        if vendor is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        email_value = update_data.pop(
            "primary_contact_email", None
        )

        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(vendor, field, value)

        if email_value is not None:
            self._set_encrypted_email(vendor, email_value)

        await self._session.flush()
        logger.info("vendor_updated", vendor_id=str(vendor_id))
        return self._to_response(vendor)

    # ── Delete (soft) ──────────────────────────────────────

    async def delete_vendor(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> bool:
        """Soft-delete a vendor. Returns False if not found."""
        vendor = await self._get_vendor_or_none(
            tenant_id, vendor_id
        )
        if vendor is None:
            return False

        vendor.deleted_at = datetime.now(UTC)
        await self._session.flush()
        logger.info("vendor_deleted", vendor_id=str(vendor_id))
        return True

    # ── Bulk Import ────────────────────────────────────────

    async def bulk_import(
        self,
        tenant_id: uuid.UUID,
        csv_data: str,
    ) -> BulkImportResult:
        """Parse CSV rows and create vendors. Track errors per row."""
        errors: list[BulkImportError] = []
        success_count = 0

        try:
            reader = csv.DictReader(io.StringIO(csv_data))
        except Exception as exc:
            return BulkImportResult(
                error_count=1,
                errors=[
                    BulkImportError(
                        row=0, message=f"CSV parse error: {exc}"
                    )
                ],
            )

        for row_num, row in enumerate(reader, start=2):
            try:
                vendor_data = self._parse_csv_row(row)
                await self.create_vendor(tenant_id, vendor_data)
                success_count += 1
            except Exception as exc:
                errors.append(
                    BulkImportError(
                        row=row_num, message=str(exc)
                    )
                )

        logger.info(
            "bulk_import_complete",
            success=success_count,
            errors=len(errors),
        )
        return BulkImportResult(
            success_count=success_count,
            error_count=len(errors),
            errors=errors,
        )

    # ── Calculate Tier ─────────────────────────────────────

    async def calculate_tier(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> str | None:
        """Calculate and persist tier based on vendor attributes."""
        vendor = await self._get_vendor_or_none(
            tenant_id, vendor_id
        )
        if vendor is None:
            return None

        tier = self._compute_tier(vendor)
        vendor.tier = tier
        await self._session.flush()
        logger.info(
            "tier_calculated",
            vendor_id=str(vendor_id),
            tier=tier,
        )
        return tier

    # ── Contacts ───────────────────────────────────────────

    async def add_contact(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
        data: VendorContactCreate,
    ) -> VendorContactResponse | None:
        """Add a contact to a vendor."""
        vendor = await self._get_vendor_or_none(
            tenant_id, vendor_id
        )
        if vendor is None:
            return None

        contact = VendorContact(
            tenant_id=tenant_id,
            vendor_id=vendor_id,
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
            is_primary=data.is_primary,
            portal_access=data.portal_access,
        )
        self._set_contact_pii(contact, data.email, data.phone)
        self._session.add(contact)
        await self._session.flush()
        logger.info(
            "vendor_contact_added",
            vendor_id=str(vendor_id),
        )
        return self._to_contact_response(contact)

    async def list_contacts(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> list[VendorContactResponse] | None:
        """List contacts for a vendor. None if vendor not found."""
        vendor = await self._get_vendor_or_none(
            tenant_id, vendor_id
        )
        if vendor is None:
            return None

        result = await self._session.execute(
            select(VendorContact).where(
                VendorContact.vendor_id == vendor_id,
                VendorContact.tenant_id == tenant_id,
            )
        )
        contacts = result.scalars().all()
        return [self._to_contact_response(c) for c in contacts]

    async def update_contact(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
        contact_id: uuid.UUID,
        data: VendorContactUpdate,
    ) -> VendorContactResponse | None:
        """Update a vendor contact. None if not found."""
        result = await self._session.execute(
            select(VendorContact).where(
                VendorContact.id == contact_id,
                VendorContact.vendor_id == vendor_id,
                VendorContact.tenant_id == tenant_id,
            )
        )
        contact = result.scalars().first()
        if contact is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        email_val = update_data.pop("email", None)
        phone_val = update_data.pop("phone", None)

        for field, value in update_data.items():
            setattr(contact, field, value)

        if email_val is not None or phone_val is not None:
            self._set_contact_pii(contact, email_val, phone_val)

        await self._session.flush()
        return self._to_contact_response(contact)

    # ── Private helpers ────────────────────────────────────

    async def _get_vendor_or_none(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> Vendor | None:
        """Fetch a non-deleted vendor or return None."""
        result = await self._session.execute(
            select(Vendor).where(
                Vendor.id == vendor_id,
                Vendor.tenant_id == tenant_id,
                Vendor.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    def _set_encrypted_email(
        self,
        vendor: Vendor,
        email: str | None,
    ) -> None:
        """Encrypt primary contact email and store hash."""
        if email:
            vendor.primary_contact_email_encrypted = (
                self._encryptor.encrypt(email)
            )
            vendor.primary_contact_email_hash = (
                self._encryptor.hmac_hash(email)
            )
        else:
            vendor.primary_contact_email_encrypted = None
            vendor.primary_contact_email_hash = None

    def _set_contact_pii(
        self,
        contact: VendorContact,
        email: str | None,
        phone: str | None,
    ) -> None:
        """Encrypt contact email and phone fields."""
        if email is not None:
            contact.email_encrypted = (
                self._encryptor.encrypt(email)
            )
            contact.email_hash = self._encryptor.hmac_hash(email)
        if phone is not None:
            contact.phone_encrypted = (
                self._encryptor.encrypt(phone)
            )
            contact.phone_hash = self._encryptor.hmac_hash(phone)

    def _to_response(self, vendor: Vendor) -> VendorResponse:
        """Map a Vendor ORM object to VendorResponse."""
        email = None
        if vendor.primary_contact_email_encrypted:
            try:
                email = self._encryptor.decrypt(
                    vendor.primary_contact_email_encrypted
                )
            except Exception:
                email = None

        contacts_count = 0
        try:
            contacts_count = len(vendor.contacts)
        except Exception:
            pass

        return VendorResponse(
            id=vendor.id,
            tenant_id=vendor.tenant_id,
            name=vendor.name,
            domain=vendor.domain,
            description=vendor.description,
            status=vendor.status,
            tier=vendor.tier,
            industry=vendor.industry,
            country=vendor.country,
            employee_count=vendor.employee_count,
            annual_revenue=vendor.annual_revenue,
            data_classification=vendor.data_classification,
            business_criticality=vendor.business_criticality,
            contract_start_date=vendor.contract_start_date,
            contract_end_date=vendor.contract_end_date,
            contract_value=vendor.contract_value,
            primary_contact_name=vendor.primary_contact_name,
            primary_contact_email=email,
            tags=vendor.tags,
            notes=vendor.notes,
            inherent_risk_score=vendor.inherent_risk_score,
            residual_risk_score=vendor.residual_risk_score,
            external_rating_score=vendor.external_rating_score,
            external_rating_provider=vendor.external_rating_provider,
            last_assessed_at=vendor.last_assessed_at,
            next_assessment_due=vendor.next_assessment_due,
            contacts_count=contacts_count,
            created_at=vendor.created_at,
            updated_at=vendor.updated_at,
        )

    def _to_detail_response(
        self, vendor: Vendor
    ) -> VendorDetailResponse:
        """Map a Vendor with relations to VendorDetailResponse."""
        email = None
        if vendor.primary_contact_email_encrypted:
            try:
                email = self._encryptor.decrypt(
                    vendor.primary_contact_email_encrypted
                )
            except Exception:
                email = None

        contacts = [
            self._to_contact_response(c)
            for c in (vendor.contacts or [])
        ]
        enrichments = [
            VendorEnrichmentResponse(
                id=e.id,
                source=e.source,
                data=e.data,
                confidence=e.confidence,
                is_current=e.is_current,
                enriched_at=e.enriched_at,
                created_at=e.created_at,
            )
            for e in (vendor.enrichments or [])
        ]

        return VendorDetailResponse(
            id=vendor.id,
            tenant_id=vendor.tenant_id,
            name=vendor.name,
            domain=vendor.domain,
            description=vendor.description,
            status=vendor.status,
            tier=vendor.tier,
            industry=vendor.industry,
            country=vendor.country,
            employee_count=vendor.employee_count,
            annual_revenue=vendor.annual_revenue,
            data_classification=vendor.data_classification,
            business_criticality=vendor.business_criticality,
            contract_start_date=vendor.contract_start_date,
            contract_end_date=vendor.contract_end_date,
            contract_value=vendor.contract_value,
            primary_contact_name=vendor.primary_contact_name,
            primary_contact_email=email,
            tags=vendor.tags,
            notes=vendor.notes,
            inherent_risk_score=vendor.inherent_risk_score,
            residual_risk_score=vendor.residual_risk_score,
            external_rating_score=vendor.external_rating_score,
            external_rating_provider=vendor.external_rating_provider,
            last_assessed_at=vendor.last_assessed_at,
            next_assessment_due=vendor.next_assessment_due,
            contacts=contacts,
            enrichments=enrichments,
            timeline=[],
            created_at=vendor.created_at,
            updated_at=vendor.updated_at,
        )

    def _to_contact_response(
        self, contact: VendorContact
    ) -> VendorContactResponse:
        """Map a VendorContact ORM object to response schema."""
        email = None
        if contact.email_encrypted:
            try:
                email = self._encryptor.decrypt(
                    contact.email_encrypted
                )
            except Exception:
                email = None

        phone = None
        if contact.phone_encrypted:
            try:
                phone = self._encryptor.decrypt(
                    contact.phone_encrypted
                )
            except Exception:
                phone = None

        return VendorContactResponse(
            id=contact.id,
            vendor_id=contact.vendor_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=email,
            phone=phone,
            role=contact.role,
            is_primary=contact.is_primary,
            portal_access=contact.portal_access,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )

    @staticmethod
    def _apply_filters(query, filters: VendorFilterParams):
        """Apply WHERE clauses for status, tier, search, tags."""
        if filters.status:
            query = query.where(
                Vendor.status == filters.status.value
            )
        if filters.tier:
            query = query.where(
                Vendor.tier == filters.tier.value
            )
        if filters.data_classification:
            query = query.where(
                Vendor.data_classification
                == filters.data_classification.value
            )
        if filters.business_criticality:
            query = query.where(
                Vendor.business_criticality
                == filters.business_criticality.value
            )
        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.where(
                or_(
                    Vendor.name.ilike(pattern),
                    Vendor.domain.ilike(pattern),
                )
            )
        if filters.tags:
            query = query.where(
                Vendor.tags.overlap(filters.tags)
            )
        return query

    @staticmethod
    def _apply_sorting(query, filters: VendorFilterParams):
        """Apply ORDER BY clause based on filter params."""
        col = getattr(Vendor, filters.sort_by, Vendor.created_at)
        if filters.sort_order.value == "desc":
            query = query.order_by(col.desc())
        else:
            query = query.order_by(col.asc())
        return query

    @staticmethod
    def _compute_tier(vendor: Vendor) -> str:
        """Derive tier from data_classification, criticality, etc."""
        score = 0

        dc_scores = {
            "restricted": 4,
            "confidential": 3,
            "internal": 2,
            "public": 1,
        }
        score += dc_scores.get(
            vendor.data_classification or "", 0
        )

        bc_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        score += bc_scores.get(
            vendor.business_criticality or "", 0
        )

        if vendor.contract_value:
            if vendor.contract_value >= 1_000_000:
                score += 4
            elif vendor.contract_value >= 500_000:
                score += 3
            elif vendor.contract_value >= 100_000:
                score += 2
            else:
                score += 1

        if vendor.employee_count:
            if vendor.employee_count >= 10_000:
                score += 2
            elif vendor.employee_count >= 1_000:
                score += 1

        if score >= 10:
            return "critical"
        if score >= 7:
            return "high"
        if score >= 4:
            return "medium"
        if score >= 1:
            return "low"
        return "unclassified"

    @staticmethod
    def _parse_csv_row(row: dict) -> VendorCreate:
        """Convert a CSV dict row into a VendorCreate schema."""
        employee_count = None
        raw_ec = row.get("employee_count", "").strip()
        if raw_ec:
            employee_count = int(raw_ec)

        contract_value = None
        raw_cv = row.get("contract_value", "").strip()
        if raw_cv:
            contract_value = Decimal(raw_cv)

        return VendorCreate(
            name=row.get("name", "").strip(),
            domain=row.get("domain", "").strip() or None,
            description=row.get("description", "").strip()
            or None,
            industry=row.get("industry", "").strip() or None,
            country=row.get("country", "").strip() or None,
            employee_count=employee_count,
            contract_value=contract_value,
            primary_contact_name=row.get(
                "primary_contact_name", ""
            ).strip()
            or None,
            primary_contact_email=row.get(
                "primary_contact_email", ""
            ).strip()
            or None,
            tags=row.get("tags", "").strip().split(",")
            if row.get("tags", "").strip()
            else None,
        )
