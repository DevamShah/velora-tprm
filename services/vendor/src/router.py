"""
Vendor API endpoints — CRUD, bulk import, tier calculation, contacts.

All endpoints require authentication. Permissions enforced per-route.
"""

from __future__ import annotations

import uuid
from typing import Annotated, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.db import get_db
from velora_common.auth import (
    get_current_user,
    require_permission,
)
from velora_common.logging import get_logger
from .schemas import (
    BulkImportRequest,
    BulkImportResult,
    VendorContactCreate,
    VendorContactResponse,
    VendorContactUpdate,
    VendorCreate,
    VendorDetailResponse,
    VendorFilterParams,
    VendorListResponse,
    VendorResponse,
    VendorUpdate,
)
from .service import VendorService

logger = get_logger(__name__)

router = APIRouter(prefix="/vendors", tags=["vendors"])


# ── Create Vendor ──────────────────────────────────────────


@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("vendors.write"))
    ],
)
async def create_vendor(
    body: VendorCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> VendorResponse:
    """Create a new vendor record."""
    service = VendorService(session)
    return await service.create_vendor(
        current_user["tenant_id"], body
    )


# ── List Vendors ───────────────────────────────────────────


@router.get(
    "",
    response_model=VendorListResponse,
    dependencies=[
        Depends(require_permission("vendors.read"))
    ],
)
async def list_vendors(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    status_filter: Optional[str] = Query(
        None, alias="status"
    ),
    tier: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=255),
    tags: Optional[str] = Query(None),
    data_classification: Optional[str] = Query(None),
    business_criticality: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> VendorListResponse:
    """List vendors with filtering, sorting, and pagination."""
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]

    filters = VendorFilterParams(
        status=status_filter,
        tier=tier,
        search=search,
        tags=tag_list,
        data_classification=data_classification,
        business_criticality=business_criticality,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    service = VendorService(session)
    return await service.list_vendors(
        current_user["tenant_id"], filters
    )


# ── Get Vendor Detail ──────────────────────────────────────


@router.get(
    "/{vendor_id}",
    response_model=VendorDetailResponse,
    dependencies=[
        Depends(require_permission("vendors.read"))
    ],
)
async def get_vendor(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> VendorDetailResponse:
    """Fetch full vendor detail with contacts and enrichment."""
    service = VendorService(session)
    result = await service.get_vendor(
        current_user["tenant_id"], vendor_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    return result


# ── Update Vendor ──────────────────────────────────────────


@router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
    dependencies=[
        Depends(require_permission("vendors.write"))
    ],
)
async def update_vendor(
    vendor_id: uuid.UUID,
    body: VendorUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> VendorResponse:
    """Update an existing vendor."""
    service = VendorService(session)
    result = await service.update_vendor(
        current_user["tenant_id"], vendor_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    return result


# ── Delete Vendor ──────────────────────────────────────────


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permission("vendors.delete"))
    ],
)
async def delete_vendor(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> None:
    """Soft-delete a vendor."""
    service = VendorService(session)
    deleted = await service.delete_vendor(
        current_user["tenant_id"], vendor_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )


# ── Bulk Import ────────────────────────────────────────────


@router.post(
    "/bulk-import",
    response_model=BulkImportResult,
    dependencies=[
        Depends(require_permission("vendors.write"))
    ],
)
async def bulk_import(
    body: BulkImportRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> BulkImportResult:
    """Import vendors from CSV data."""
    service = VendorService(session)
    return await service.bulk_import(
        current_user["tenant_id"], body.csv_data
    )


# ── Calculate Tier ─────────────────────────────────────────


@router.post(
    "/{vendor_id}/calculate-tier",
    response_model=dict,
    dependencies=[
        Depends(require_permission("vendors.write"))
    ],
)
async def calculate_tier(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> dict:
    """Recalculate and persist vendor tier classification."""
    service = VendorService(session)
    tier = await service.calculate_tier(
        current_user["tenant_id"], vendor_id
    )
    if tier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    return {"vendor_id": str(vendor_id), "tier": tier}


# ── List Contacts ──────────────────────────────────────────


@router.get(
    "/{vendor_id}/contacts",
    response_model=List[VendorContactResponse],
    dependencies=[
        Depends(require_permission("vendors.read"))
    ],
)
async def list_contacts(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[VendorContactResponse]:
    """List all contacts for a vendor."""
    service = VendorService(session)
    result = await service.list_contacts(
        current_user["tenant_id"], vendor_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    return result


# ── Add Contact ────────────────────────────────────────────


@router.post(
    "/{vendor_id}/contacts",
    response_model=VendorContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("vendors.write"))
    ],
)
async def add_contact(
    vendor_id: uuid.UUID,
    body: VendorContactCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> VendorContactResponse:
    """Add a contact to a vendor."""
    service = VendorService(session)
    result = await service.add_contact(
        current_user["tenant_id"], vendor_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    return result


# ── Update Contact ─────────────────────────────────────────


@router.put(
    "/{vendor_id}/contacts/{contact_id}",
    response_model=VendorContactResponse,
    dependencies=[
        Depends(require_permission("vendors.write"))
    ],
)
async def update_contact(
    vendor_id: uuid.UUID,
    contact_id: uuid.UUID,
    body: VendorContactUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> VendorContactResponse:
    """Update a vendor contact."""
    service = VendorService(session)
    result = await service.update_contact(
        current_user["tenant_id"],
        vendor_id,
        contact_id,
        body,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return result
