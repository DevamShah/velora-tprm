"""
Unit tests for EvidenceService.

The session is mocked, so no database is touched. Object storage is
not called by this service — upload_evidence only mints an S3 key and
a mock presigned URL — but the storage client is patched defensively
in test_upload_evidence_makes_no_storage_calls to prove that.
"""

from __future__ import annotations

import sys
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.evidence.models import (
    Evidence,
    EvidenceControlMapping,
    EvidenceExtraction,
)
from app.modules.evidence.schemas import (
    DocumentType,
    EvidenceFilterParams,
    EvidenceStatus,
    EvidenceUploadRequest,
    SortOrder,
)
from app.modules.evidence.service import EvidenceService

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000100")
ASSESSMENT_ID = uuid.UUID("00000000-0000-4000-a000-000000000600")
EVIDENCE_ID = uuid.UUID("00000000-0000-4000-a000-000000000700")
EXTRACTION_ID = uuid.UUID("00000000-0000-4000-a000-000000000800")
MAPPING_ID = uuid.UUID("00000000-0000-4000-a000-000000000900")
CLAUSE_ID = uuid.UUID("00000000-0000-4000-a000-000000000401")


def _make_evidence(**overrides) -> Evidence:
    """Create an Evidence ORM object with sensible defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=EVIDENCE_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        assessment_id=None,
        filename="soc2-report.pdf",
        file_size=204800,
        mime_type="application/pdf",
        s3_key=f"evidence/{TENANT_ID}/{VENDOR_ID}/x/soc2-report.pdf",
        document_type="soc2",
        status="uploaded",
        parsed_content=None,
        extraction_summary=None,
        classification_confidence=None,
        uploaded_by=USER_ID,
        deleted_at=None,
        extractions=[],
        control_mappings=[],
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    ev = MagicMock(spec=Evidence)
    for k, v in defaults.items():
        setattr(ev, k, v)
    return ev


def _make_extraction(**overrides) -> EvidenceExtraction:
    """Create an EvidenceExtraction ORM object with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=EXTRACTION_ID,
        tenant_id=TENANT_ID,
        evidence_id=EVIDENCE_ID,
        field_name="auditor",
        field_value="Deloitte LLP",
        confidence=0.98,
        page_number=1,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    ext = MagicMock(spec=EvidenceExtraction)
    for k, v in defaults.items():
        setattr(ext, k, v)
    return ext


def _make_mapping(**overrides) -> EvidenceControlMapping:
    """Create an EvidenceControlMapping ORM object with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=MAPPING_ID,
        tenant_id=TENANT_ID,
        evidence_id=EVIDENCE_ID,
        clause_id=CLAUSE_ID,
        coverage_type="full",
        confidence=0.77,
        verified=False,
        verified_by=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    mapping = MagicMock(spec=EvidenceControlMapping)
    for k, v in defaults.items():
        setattr(mapping, k, v)
    return mapping


def _mock_execute_result(items, scalar=None):
    """Mock execute result exposing scalars().first()/all() and scalar()."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.scalar.return_value = (
        scalar if scalar is not None else len(items)
    )
    return result


@pytest.fixture
def mock_session():
    """Async mock session that assigns ids on flush, like a real one."""
    session = AsyncMock()
    added: list = []
    session.added = added
    session.add = MagicMock(side_effect=added.append)

    async def _flush() -> None:
        for obj in added:
            if getattr(obj, "id", None) is None:
                obj.id = EVIDENCE_ID

    session.flush = AsyncMock(side_effect=_flush)
    return session


@pytest.fixture
def service(mock_session):
    """EvidenceService bound to the mocked session."""
    return EvidenceService(mock_session)


# -- upload_evidence ------------------------------------------------


@pytest.mark.asyncio
async def test_upload_evidence_persists_record_and_returns_url(
    service, mock_session
):
    """upload_evidence stores the row and mints a matching s3 key/URL."""
    data = EvidenceUploadRequest(
        vendor_id=VENDOR_ID,
        assessment_id=ASSESSMENT_ID,
        filename="soc2-report.pdf",
        file_size=204800,
        mime_type="application/pdf",
        document_type=DocumentType.soc2,
    )

    result = await service.upload_evidence(TENANT_ID, data, USER_ID)

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()

    stored = mock_session.added[0]
    assert isinstance(stored, Evidence)
    assert stored.tenant_id == TENANT_ID
    assert stored.vendor_id == VENDOR_ID
    assert stored.assessment_id == ASSESSMENT_ID
    assert stored.filename == "soc2-report.pdf"
    assert stored.file_size == 204800
    assert stored.mime_type == "application/pdf"
    assert stored.document_type == "soc2"
    assert stored.status == "uploaded"
    assert stored.uploaded_by == USER_ID

    prefix = f"evidence/{TENANT_ID}/{VENDOR_ID}/"
    assert result.s3_key.startswith(prefix)
    assert result.s3_key.endswith("/soc2-report.pdf")
    assert result.s3_key == stored.s3_key
    assert result.evidence_id == EVIDENCE_ID
    assert result.upload_url == (
        f"https://s3.mock.velora.io/{result.s3_key}"
        "?X-Amz-SignedHeaders=host"
    )


@pytest.mark.asyncio
async def test_upload_evidence_s3_key_segment_is_a_uuid(
    service, mock_session
):
    """The middle path segment is a fresh UUID, unique per upload."""
    data = EvidenceUploadRequest(
        vendor_id=VENDOR_ID,
        filename="policy.pdf",
        file_size=10,
        mime_type="application/pdf",
    )

    first = await service.upload_evidence(TENANT_ID, data, USER_ID)
    second = await service.upload_evidence(TENANT_ID, data, USER_ID)

    parts = first.s3_key.split("/")
    assert parts[0] == "evidence"
    assert parts[1] == str(TENANT_ID)
    assert parts[2] == str(VENDOR_ID)
    # Raises ValueError if not a UUID.
    uuid.UUID(parts[3])
    assert parts[4] == "policy.pdf"
    assert first.s3_key != second.s3_key


@pytest.mark.asyncio
async def test_upload_evidence_defaults_document_type_to_other(
    service, mock_session
):
    """Omitting document_type stores the 'other' enum value."""
    data = EvidenceUploadRequest(
        vendor_id=VENDOR_ID,
        filename="misc.txt",
        file_size=1,
        mime_type="text/plain",
    )

    await service.upload_evidence(TENANT_ID, data, USER_ID)

    stored = mock_session.added[0]
    assert stored.document_type == "other"
    assert stored.assessment_id is None


@pytest.mark.asyncio
async def test_upload_evidence_makes_no_storage_calls(
    service, mock_session
):
    """The upload URL is mocked in-process — boto3 is never touched."""
    fake_boto3 = MagicMock()
    with patch.dict(sys.modules, {"boto3": fake_boto3}):
        data = EvidenceUploadRequest(
            vendor_id=VENDOR_ID,
            filename="report.pdf",
            file_size=99,
            mime_type="application/pdf",
        )
        result = await service.upload_evidence(
            TENANT_ID, data, USER_ID
        )

    fake_boto3.client.assert_not_called()
    assert result.upload_url.startswith("https://s3.mock.velora.io/")


# -- get_evidence ---------------------------------------------------


@pytest.mark.asyncio
async def test_get_evidence_returns_none_when_missing(
    service, mock_session
):
    """get_evidence returns None for an unknown / other-tenant id."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service.get_evidence(TENANT_ID, EVIDENCE_ID) is None


@pytest.mark.asyncio
async def test_get_evidence_returns_detail_with_children(
    service, mock_session
):
    """Extractions and control mappings are mapped into the detail."""
    ev = _make_evidence(
        status="parsed",
        classification_confidence=0.92,
        parsed_content={"pages": 12},
        extraction_summary={"fields_extracted": 4},
        extractions=[_make_extraction()],
        control_mappings=[_make_mapping()],
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([ev])
    )

    result = await service.get_evidence(TENANT_ID, EVIDENCE_ID)

    assert result is not None
    assert result.id == EVIDENCE_ID
    assert result.tenant_id == TENANT_ID
    assert result.filename == "soc2-report.pdf"
    assert result.status == "parsed"
    assert result.classification_confidence == 0.92
    assert result.parsed_content == {"pages": 12}
    assert result.extraction_summary == {"fields_extracted": 4}

    assert len(result.extractions) == 1
    assert result.extractions[0].field_name == "auditor"
    assert result.extractions[0].field_value == "Deloitte LLP"
    assert result.extractions[0].confidence == 0.98
    assert result.extractions[0].page_number == 1

    assert len(result.control_mappings) == 1
    assert result.control_mappings[0].clause_id == CLAUSE_ID
    assert result.control_mappings[0].coverage_type == "full"
    assert result.control_mappings[0].verified is False


def test_to_detail_tolerates_null_relations():
    """_to_detail treats None relations as empty lists."""
    ev = _make_evidence(extractions=None, control_mappings=None)

    detail = EvidenceService._to_detail(ev)

    assert detail.extractions == []
    assert detail.control_mappings == []


def test_to_response_maps_summary_fields():
    """_to_response copies the list-view columns verbatim."""
    ev = _make_evidence(
        assessment_id=ASSESSMENT_ID,
        status="mapped",
        classification_confidence=0.5,
    )

    resp = EvidenceService._to_response(ev)

    assert resp.id == EVIDENCE_ID
    assert resp.assessment_id == ASSESSMENT_ID
    assert resp.mime_type == "application/pdf"
    assert resp.file_size == 204800
    assert resp.document_type == "soc2"
    assert resp.status == "mapped"
    assert resp.classification_confidence == 0.5
    assert resp.uploaded_by == USER_ID


# -- list_evidence --------------------------------------------------


@pytest.mark.asyncio
async def test_list_evidence_paginates_and_sorts_desc(
    service, mock_session
):
    """Default filters page from 1 and sort created_at descending."""
    ev = _make_evidence()
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([], scalar=37),
            _mock_execute_result([ev]),
        ]
    )

    filters = EvidenceFilterParams(page=2, page_size=15)
    result = await service.list_evidence(TENANT_ID, filters)

    assert result.total == 37
    assert result.page == 2
    assert result.page_size == 15
    assert len(result.items) == 1
    assert result.items[0].filename == "soc2-report.pdf"

    stmt = mock_session.execute.await_args_list[1].args[0]
    assert stmt._limit_clause.value == 15
    assert stmt._offset_clause.value == 15
    assert "ORDER BY evidence.created_at DESC" in str(stmt)


@pytest.mark.asyncio
async def test_list_evidence_sorts_ascending_on_chosen_column(
    service, mock_session
):
    """sort_by/sort_order drive the ORDER BY clause."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([], scalar=0),
            _mock_execute_result([]),
        ]
    )

    filters = EvidenceFilterParams(
        sort_by="filename", sort_order=SortOrder.asc
    )
    result = await service.list_evidence(TENANT_ID, filters)

    assert result.items == []
    stmt = mock_session.execute.await_args_list[1].args[0]
    assert "ORDER BY evidence.filename ASC" in str(stmt)


@pytest.mark.asyncio
async def test_list_evidence_null_count_coerced_to_zero(
    service, mock_session
):
    """A NULL count from the DB becomes a total of 0, not None."""
    null_count = MagicMock()
    null_count.scalar.return_value = None
    mock_session.execute = AsyncMock(
        side_effect=[null_count, _mock_execute_result([])]
    )

    result = await service.list_evidence(
        TENANT_ID, EvidenceFilterParams()
    )

    assert result.total == 0


@pytest.mark.asyncio
async def test_list_evidence_applies_all_filters(
    service, mock_session
):
    """vendor_id, document_type and status all reach the WHERE clause."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([], scalar=0),
            _mock_execute_result([]),
        ]
    )

    filters = EvidenceFilterParams(
        vendor_id=VENDOR_ID,
        document_type=DocumentType.pen_test,
        status=EvidenceStatus.parsed,
    )
    await service.list_evidence(TENANT_ID, filters)

    sql = str(mock_session.execute.await_args_list[1].args[0])
    assert "evidence.vendor_id = " in sql
    assert "evidence.document_type = " in sql
    assert "evidence.status = " in sql
    assert "evidence.deleted_at IS NULL" in sql


def test_apply_filters_without_filters_is_a_noop():
    """_apply_filters leaves the query untouched when nothing is set."""
    from sqlalchemy import select

    base = select(Evidence)
    out = EvidenceService._apply_filters(base, EvidenceFilterParams())

    assert str(out) == str(base)


def test_apply_filters_adds_only_requested_predicates():
    """Only the supplied filters become WHERE predicates."""
    from sqlalchemy import select

    base = select(Evidence)
    out = EvidenceService._apply_filters(
        base,
        EvidenceFilterParams(document_type=DocumentType.iso_cert),
    )

    sql = str(out)
    assert "evidence.document_type = " in sql
    assert "evidence.vendor_id = " not in sql
    assert "evidence.status = " not in sql


# -- process_evidence -----------------------------------------------


@pytest.mark.asyncio
async def test_process_evidence_returns_none_when_missing(
    service, mock_session
):
    """process_evidence does no work for an unknown evidence id."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.process_evidence(TENANT_ID, EVIDENCE_ID)

    assert result is None
    mock_session.add.assert_not_called()
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_evidence_writes_extractions_and_summary(
    service, mock_session
):
    """A soc2 doc yields 4 extractions and a parsed status/summary."""
    ev = _make_evidence()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([ev])
    )
    sentinel = MagicMock()

    with patch.object(
        service,
        "get_evidence",
        new_callable=AsyncMock,
        return_value=sentinel,
    ) as mock_get:
        result = await service.process_evidence(
            TENANT_ID, EVIDENCE_ID
        )

    assert result is sentinel
    mock_get.assert_awaited_once_with(TENANT_ID, EVIDENCE_ID)

    assert ev.status == "parsed"
    assert ev.parsed_content == {
        "pages": 12,
        "sections": ["scope", "controls", "audit"],
    }
    assert ev.extraction_summary == {
        "fields_extracted": 4,
        "avg_confidence": 0.87,
    }
    assert ev.classification_confidence == 0.92

    assert mock_session.add.call_count == 4
    assert all(
        isinstance(o, EvidenceExtraction) for o in mock_session.added
    )
    assert [o.field_name for o in mock_session.added] == [
        "audit_period",
        "auditor",
        "opinion_type",
        "scope",
    ]
    # Once before extraction generation, once after.
    assert mock_session.flush.await_count == 2


@pytest.mark.asyncio
async def test_process_evidence_unknown_doc_type_uses_defaults(
    service, mock_session
):
    """An unmapped document type falls back to the generic field set."""
    ev = _make_evidence(document_type="contract")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([ev])
    )

    with patch.object(
        service, "get_evidence", new_callable=AsyncMock
    ):
        await service.process_evidence(TENANT_ID, EVIDENCE_ID)

    assert ev.extraction_summary["fields_extracted"] == 3
    assert [o.field_name for o in mock_session.added] == [
        "document_title",
        "effective_date",
        "version",
    ]


# -- _generate_mock_extractions -------------------------------------


@pytest.mark.parametrize(
    ("doc_type", "expected"),
    [
        (
            "soc2",
            ["audit_period", "auditor", "opinion_type", "scope"],
        ),
        (
            "iso_cert",
            [
                "certificate_number",
                "standard",
                "valid_until",
                "certifying_body",
            ],
        ),
        (
            "pen_test",
            [
                "test_date",
                "tester",
                "critical_findings",
                "high_findings",
            ],
        ),
        (
            "policy",
            ["document_title", "effective_date", "version"],
        ),
    ],
)
def test_generate_mock_extractions_per_doc_type(doc_type, expected):
    """Each document type maps to its own extraction field set."""
    rows = EvidenceService._generate_mock_extractions(
        TENANT_ID, EVIDENCE_ID, doc_type
    )

    assert [r.field_name for r in rows] == expected
    assert all(r.tenant_id == TENANT_ID for r in rows)
    assert all(r.evidence_id == EVIDENCE_ID for r in rows)
    assert all(0.0 < r.confidence <= 1.0 for r in rows)
    assert all(r.page_number >= 1 for r in rows)


def test_generate_mock_extractions_values_for_iso_cert():
    """iso_cert extraction values and confidences are exact."""
    rows = EvidenceService._generate_mock_extractions(
        TENANT_ID, EVIDENCE_ID, "iso_cert"
    )

    by_name = {r.field_name: r for r in rows}
    assert by_name["standard"].field_value == "ISO/IEC 27001:2022"
    assert by_name["standard"].confidence == 0.99
    assert by_name["valid_until"].field_value == "2027-03-15"
    assert by_name["certifying_body"].field_value == "BSI Group"


# -- get_mappings ---------------------------------------------------


@pytest.mark.asyncio
async def test_get_mappings_returns_none_when_evidence_missing(
    service, mock_session
):
    """None (not []) signals a missing evidence record to the router."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.get_mappings(TENANT_ID, EVIDENCE_ID)

    assert result is None
    assert mock_session.execute.await_count == 1


@pytest.mark.asyncio
async def test_get_mappings_returns_mapping_responses(
    service, mock_session
):
    """Existing evidence yields one response per mapping row."""
    ev = _make_evidence()
    mapping = _make_mapping(verified=True, verified_by=USER_ID)
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([ev]),
            _mock_execute_result([mapping]),
        ]
    )

    result = await service.get_mappings(TENANT_ID, EVIDENCE_ID)

    assert len(result) == 1
    assert result[0].id == MAPPING_ID
    assert result[0].evidence_id == EVIDENCE_ID
    assert result[0].clause_id == CLAUSE_ID
    assert result[0].coverage_type == "full"
    assert result[0].confidence == 0.77
    assert result[0].verified is True
    assert result[0].verified_by == USER_ID


@pytest.mark.asyncio
async def test_get_mappings_empty_list_for_unmapped_evidence(
    service, mock_session
):
    """Evidence with no mappings returns an empty list, not None."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([_make_evidence()]),
            _mock_execute_result([]),
        ]
    )

    result = await service.get_mappings(TENANT_ID, EVIDENCE_ID)

    assert result == []


# -- verify_mapping -------------------------------------------------


@pytest.mark.asyncio
async def test_verify_mapping_sets_verifier(service, mock_session):
    """Verifying records who verified it and flushes."""
    mapping = _make_mapping()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([mapping])
    )

    result = await service.verify_mapping(
        TENANT_ID, EVIDENCE_ID, MAPPING_ID, True, USER_ID
    )

    assert mapping.verified is True
    assert mapping.verified_by == USER_ID
    assert result.verified is True
    assert result.verified_by == USER_ID
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_mapping_rejection_clears_verifier(
    service, mock_session
):
    """Rejecting a mapping wipes verified_by rather than recording it."""
    mapping = _make_mapping(verified=True, verified_by=USER_ID)
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([mapping])
    )

    result = await service.verify_mapping(
        TENANT_ID, EVIDENCE_ID, MAPPING_ID, False, USER_ID
    )

    assert mapping.verified is False
    assert mapping.verified_by is None
    assert result.verified is False
    assert result.verified_by is None


@pytest.mark.asyncio
async def test_verify_mapping_returns_none_when_missing(
    service, mock_session
):
    """An unknown mapping id returns None and does not flush."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.verify_mapping(
        TENANT_ID, EVIDENCE_ID, MAPPING_ID, True, USER_ID
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# -- delete_evidence ------------------------------------------------


@pytest.mark.asyncio
async def test_delete_evidence_soft_deletes(service, mock_session):
    """delete_evidence stamps deleted_at instead of removing the row."""
    ev = _make_evidence()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([ev])
    )
    before = datetime.now(UTC)

    result = await service.delete_evidence(TENANT_ID, EVIDENCE_ID)

    assert result is True
    assert ev.deleted_at is not None
    assert ev.deleted_at >= before
    mock_session.delete.assert_not_called()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_evidence_returns_false_when_missing(
    service, mock_session
):
    """Deleting an unknown id is a no-op returning False."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.delete_evidence(TENANT_ID, EVIDENCE_ID)

    assert result is False
    mock_session.flush.assert_not_awaited()


# -- _get_or_none ---------------------------------------------------


@pytest.mark.asyncio
async def test_get_or_none_scopes_query_to_tenant_and_not_deleted(
    service, mock_session
):
    """The lookup filters on id, tenant and a NULL deleted_at."""
    ev = _make_evidence()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([ev])
    )

    result = await service._get_or_none(TENANT_ID, EVIDENCE_ID)

    assert result is ev
    sql = str(mock_session.execute.await_args_list[0].args[0])
    assert "evidence.id = " in sql
    assert "evidence.tenant_id = " in sql
    assert "evidence.deleted_at IS NULL" in sql
