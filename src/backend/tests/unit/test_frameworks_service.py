"""
Unit tests for FrameworkService.

Frameworks are global reference data, so there is no tenant scoping
and no encryption. Every test mocks the async session and asserts on
the real objects the service builds from the rows it is handed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.frameworks.models import (
    ControlMapping,
    Framework,
    FrameworkClause,
)
from app.modules.frameworks.service import FrameworkService

FRAMEWORK_ID = uuid.UUID("00000000-0000-4000-a000-000000000301")
FRAMEWORK_ID_2 = uuid.UUID("00000000-0000-4000-a000-000000000302")
CLAUSE_ID = uuid.UUID("00000000-0000-4000-a000-000000000401")
CHILD_CLAUSE_ID = uuid.UUID("00000000-0000-4000-a000-000000000402")
GRANDCHILD_CLAUSE_ID = uuid.UUID("00000000-0000-4000-a000-000000000403")
OTHER_CLAUSE_ID = uuid.UUID("00000000-0000-4000-a000-000000000404")
MAPPING_ID = uuid.UUID("00000000-0000-4000-a000-000000000501")


def _make_framework(**overrides) -> Framework:
    """Create a Framework ORM object with sensible defaults."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=FRAMEWORK_ID,
        name="ISO 27001",
        version="2022",
        description="Information security management",
        framework_type="certification",
        source_url="https://iso.org/27001",
        clause_count=93,
        status="active",
        structure={"sections": ["A.5", "A.6"]},
        clauses=[],
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    fw = MagicMock(spec=Framework)
    for k, v in defaults.items():
        setattr(fw, k, v)
    return fw


def _make_clause(**overrides) -> FrameworkClause:
    """Create a FrameworkClause ORM object with defaults."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=CLAUSE_ID,
        framework_id=FRAMEWORK_ID,
        parent_clause_id=None,
        clause_number="A.5",
        title="Organizational controls",
        description="Policies for information security",
        domain_tags=["governance"],
        depth=0,
        order_index=0,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    clause = MagicMock(spec=FrameworkClause)
    for k, v in defaults.items():
        setattr(clause, k, v)
    return clause


def _make_mapping(**overrides) -> ControlMapping:
    """Create a ControlMapping ORM object with defaults."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=MAPPING_ID,
        source_clause_id=CLAUSE_ID,
        target_clause_id=OTHER_CLAUSE_ID,
        mapping_type="equivalent",
        confidence=0.91,
        source_type="olir",
        verified=True,
        verified_by=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    mapping = MagicMock(spec=ControlMapping)
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
        scalar if scalar is not None else (items[0] if items else None)
    )
    return result


def _mock_rows_result(rows):
    """Mock execute result that is iterated directly (GROUP BY rows)."""
    result = MagicMock()
    result.__iter__.return_value = iter(rows)
    return result


@pytest.fixture
def mock_session():
    """Async mock session."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    """FrameworkService bound to the mocked session."""
    return FrameworkService(mock_session)


# -- list_frameworks ------------------------------------------------


@pytest.mark.asyncio
async def test_list_frameworks_maps_every_column(service, mock_session):
    """list_frameworks returns one response per row with fields copied."""
    fw_a = _make_framework()
    fw_b = _make_framework(
        id=FRAMEWORK_ID_2,
        name="SOC 2",
        version="2017 TSC",
        clause_count=64,
        framework_type="attestation",
        status="draft",
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([fw_a, fw_b])
    )

    result = await service.list_frameworks()

    assert result.total == 2
    assert [f.name for f in result.items] == ["ISO 27001", "SOC 2"]
    assert result.items[0].id == FRAMEWORK_ID
    assert result.items[0].version == "2022"
    assert result.items[0].clause_count == 93
    assert result.items[0].source_url == "https://iso.org/27001"
    assert result.items[1].framework_type == "attestation"
    assert result.items[1].status == "draft"
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_frameworks_empty(service, mock_session):
    """list_frameworks reports total 0 when no frameworks exist."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.list_frameworks()

    assert result.total == 0
    assert result.items == []


# -- get_framework --------------------------------------------------


@pytest.mark.asyncio
async def test_get_framework_returns_none_when_missing(
    service, mock_session
):
    """get_framework short-circuits to None without loading clauses."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.get_framework(FRAMEWORK_ID)

    assert result is None
    # Only the framework lookup ran — no clause query.
    assert mock_session.execute.await_count == 1


@pytest.mark.asyncio
async def test_get_framework_includes_clause_tree(service, mock_session):
    """get_framework attaches the nested clause tree to the detail."""
    fw = _make_framework()
    parent = _make_clause()
    child = _make_clause(
        id=CHILD_CLAUSE_ID,
        parent_clause_id=CLAUSE_ID,
        clause_number="A.5.1",
        title="Policies",
        depth=1,
        order_index=1,
    )
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([fw]),
            _mock_execute_result([parent, child]),
        ]
    )

    result = await service.get_framework(FRAMEWORK_ID)

    assert result is not None
    assert result.name == "ISO 27001"
    assert result.structure == {"sections": ["A.5", "A.6"]}
    assert len(result.clauses) == 1
    assert result.clauses[0].clause_number == "A.5"
    assert [c.clause_number for c in result.clauses[0].children] == [
        "A.5.1"
    ]
    assert mock_session.execute.await_count == 2


# -- get_clause_tree / _build_tree ----------------------------------


@pytest.mark.asyncio
async def test_get_clause_tree_nests_three_levels(service, mock_session):
    """get_clause_tree builds a parent → child → grandchild chain."""
    parent = _make_clause()
    child = _make_clause(
        id=CHILD_CLAUSE_ID,
        parent_clause_id=CLAUSE_ID,
        clause_number="A.5.1",
        depth=1,
        order_index=1,
    )
    grandchild = _make_clause(
        id=GRANDCHILD_CLAUSE_ID,
        parent_clause_id=CHILD_CLAUSE_ID,
        clause_number="A.5.1.1",
        depth=2,
        order_index=2,
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([parent, child, grandchild])
    )

    tree = await service.get_clause_tree(FRAMEWORK_ID)

    assert len(tree) == 1
    root = tree[0]
    assert root.id == CLAUSE_ID
    assert root.domain_tags == ["governance"]
    assert len(root.children) == 1
    assert root.children[0].id == CHILD_CLAUSE_ID
    assert root.children[0].children[0].clause_number == "A.5.1.1"
    assert root.children[0].children[0].depth == 2


def test_build_tree_empty_returns_no_roots():
    """_build_tree tolerates an empty clause list."""
    assert FrameworkService._build_tree([]) == []


def test_build_tree_dangling_parent_becomes_root():
    """A clause whose parent is not in the set is promoted to a root."""
    orphan = _make_clause(
        id=CHILD_CLAUSE_ID,
        parent_clause_id=uuid.uuid4(),
        clause_number="A.9.9",
        depth=1,
    )
    sibling = _make_clause()

    roots = FrameworkService._build_tree([sibling, orphan])

    assert len(roots) == 2
    assert {r.clause_number for r in roots} == {"A.5", "A.9.9"}
    assert all(r.children == [] for r in roots)


def test_build_tree_preserves_input_order_for_siblings():
    """Children keep the order they arrive in (query is order_index asc)."""
    parent = _make_clause()
    first = _make_clause(
        id=CHILD_CLAUSE_ID,
        parent_clause_id=CLAUSE_ID,
        clause_number="A.5.1",
        order_index=1,
    )
    second = _make_clause(
        id=GRANDCHILD_CLAUSE_ID,
        parent_clause_id=CLAUSE_ID,
        clause_number="A.5.2",
        order_index=2,
    )

    roots = FrameworkService._build_tree([parent, first, second])

    assert [c.clause_number for c in roots[0].children] == [
        "A.5.1",
        "A.5.2",
    ]


# -- get_clause_mappings / _enrich_mapping --------------------------


@pytest.mark.asyncio
async def test_get_clause_mappings_enriches_both_sides(
    service, mock_session
):
    """Each mapping is enriched with clause numbers/titles/framework."""
    mapping = _make_mapping()
    src_clause = _make_clause()
    tgt_clause = _make_clause(
        id=OTHER_CLAUSE_ID,
        framework_id=FRAMEWORK_ID_2,
        clause_number="CC1.1",
        title="Control environment",
    )
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([mapping]),
            _mock_execute_result([src_clause]),
            _mock_execute_result([], scalar="ISO 27001"),
            _mock_execute_result([tgt_clause]),
            _mock_execute_result([], scalar="SOC 2"),
        ]
    )

    result = await service.get_clause_mappings(CLAUSE_ID)

    assert len(result) == 1
    resp = result[0]
    assert resp.id == MAPPING_ID
    assert resp.mapping_type == "equivalent"
    assert resp.confidence == 0.91
    assert resp.source_type == "olir"
    assert resp.verified is True
    assert resp.source_clause_number == "A.5"
    assert resp.source_clause_title == "Organizational controls"
    assert resp.source_framework_name == "ISO 27001"
    assert resp.target_clause_number == "CC1.1"
    assert resp.target_clause_title == "Control environment"
    assert resp.target_framework_name == "SOC 2"


@pytest.mark.asyncio
async def test_get_clause_mappings_empty(service, mock_session):
    """No mappings means no enrichment queries at all."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.get_clause_mappings(CLAUSE_ID)

    assert result == []
    assert mock_session.execute.await_count == 1


@pytest.mark.asyncio
async def test_get_clause_mappings_missing_clauses_leave_names_none(
    service, mock_session
):
    """Dangling clause references produce None names, not an error."""
    mapping = _make_mapping()
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([mapping]),
            _mock_execute_result([]),  # source clause gone
            _mock_execute_result([]),  # target clause gone
        ]
    )

    result = await service.get_clause_mappings(CLAUSE_ID)

    resp = result[0]
    assert resp.source_clause_number is None
    assert resp.source_framework_name is None
    assert resp.target_clause_title is None
    # Framework-name lookups are skipped when the clause is missing.
    assert mock_session.execute.await_count == 3


@pytest.mark.asyncio
async def test_get_clause_with_fw_falls_back_to_unknown(
    service, mock_session
):
    """A clause pointing at a missing framework reports 'Unknown'."""
    clause = _make_clause()
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([clause]),
            _mock_execute_result([], scalar=None),
        ]
    )

    result = await service._get_clause_with_fw(CLAUSE_ID)

    assert result == ("A.5", "Organizational controls", "Unknown")


@pytest.mark.asyncio
async def test_get_clause_with_fw_returns_none_for_missing_clause(
    service, mock_session
):
    """_get_clause_with_fw returns None when the clause does not exist."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service._get_clause_with_fw(CLAUSE_ID) is None


# -- _get_mapping_counts --------------------------------------------


@pytest.mark.asyncio
async def test_get_mapping_counts_sums_source_and_target(
    service, mock_session
):
    """Counts from both directions are added per clause id."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_rows_result([(CLAUSE_ID, 3), (OTHER_CLAUSE_ID, 1)]),
            _mock_rows_result([(CLAUSE_ID, 2), (CHILD_CLAUSE_ID, 5)]),
        ]
    )

    counts = await service._get_mapping_counts()

    assert counts[CLAUSE_ID] == 5
    assert counts[OTHER_CLAUSE_ID] == 1
    assert counts[CHILD_CLAUSE_ID] == 5
    assert len(counts) == 3


@pytest.mark.asyncio
async def test_get_mapping_counts_empty(service, mock_session):
    """No mappings yields an empty count map."""
    mock_session.execute = AsyncMock(
        side_effect=[_mock_rows_result([]), _mock_rows_result([])]
    )

    assert await service._get_mapping_counts() == {}


# -- _get_mapped_frameworks -----------------------------------------


@pytest.mark.asyncio
async def test_get_mapped_frameworks_resolves_other_side(
    service, mock_session
):
    """For a source-side mapping the target's framework is returned."""
    mapping = _make_mapping()
    fw_map = {FRAMEWORK_ID: "ISO 27001", FRAMEWORK_ID_2: "SOC 2"}
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([mapping]),
            _mock_execute_result([], scalar=FRAMEWORK_ID_2),
        ]
    )

    names = await service._get_mapped_frameworks(CLAUSE_ID, fw_map)

    assert names == ["SOC 2"]


@pytest.mark.asyncio
async def test_get_mapped_frameworks_uses_source_when_clause_is_target(
    service, mock_session
):
    """When the clause is the target, the source clause is resolved."""
    mapping = _make_mapping(
        source_clause_id=OTHER_CLAUSE_ID,
        target_clause_id=CLAUSE_ID,
    )
    fw_map = {FRAMEWORK_ID_2: "SOC 2"}
    clause_result = _mock_execute_result([], scalar=FRAMEWORK_ID_2)
    mock_session.execute = AsyncMock(
        side_effect=[_mock_execute_result([mapping]), clause_result]
    )

    names = await service._get_mapped_frameworks(CLAUSE_ID, fw_map)

    assert names == ["SOC 2"]
    # The framework lookup was made for the *source* clause.
    clause_query = str(mock_session.execute.await_args_list[1].args[0])
    assert "framework_clauses.framework_id" in clause_query


@pytest.mark.asyncio
async def test_get_mapped_frameworks_unknown_framework_id(
    service, mock_session
):
    """A framework id missing from fw_map degrades to 'Unknown'."""
    mapping = _make_mapping()
    stray = uuid.uuid4()
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([mapping]),
            _mock_execute_result([], scalar=stray),
        ]
    )

    names = await service._get_mapped_frameworks(CLAUSE_ID, {})

    assert names == ["Unknown"]


@pytest.mark.asyncio
async def test_get_mapped_frameworks_skips_null_framework_id(
    service, mock_session
):
    """A mapping whose other clause resolves to nothing is dropped."""
    mapping = _make_mapping()
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([mapping]),
            _mock_execute_result([], scalar=None),
        ]
    )

    names = await service._get_mapped_frameworks(
        CLAUSE_ID, {FRAMEWORK_ID: "ISO 27001"}
    )

    assert names == []


@pytest.mark.asyncio
async def test_get_mapped_frameworks_no_mappings(service, mock_session):
    """No mappings means no framework names and a single query."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    names = await service._get_mapped_frameworks(CLAUSE_ID, {})

    assert names == []
    assert mock_session.execute.await_count == 1


# -- get_unified_controls -------------------------------------------


@pytest.mark.asyncio
async def test_get_unified_controls_builds_full_control(
    service, mock_session
):
    """Unified controls carry framework name, mapped names and counts."""
    clause = _make_clause(depth=1)
    fw_a = _make_framework()
    fw_b = _make_framework(id=FRAMEWORK_ID_2, name="SOC 2")
    mapping = _make_mapping()

    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([clause]),          # clauses
            _mock_execute_result([fw_a, fw_b]),      # frameworks
            _mock_rows_result([(CLAUSE_ID, 2)]),     # source counts
            _mock_rows_result([(CLAUSE_ID, 1)]),     # target counts
            _mock_execute_result([mapping]),         # mapped frameworks
            _mock_execute_result([], scalar=FRAMEWORK_ID_2),
        ]
    )

    controls = await service.get_unified_controls()

    assert len(controls) == 1
    ctl = controls[0]
    assert ctl.control_id == CLAUSE_ID
    assert ctl.clause_number == "A.5"
    assert ctl.title == "Organizational controls"
    assert ctl.description == "Policies for information security"
    assert ctl.domain_tags == ["governance"]
    assert ctl.framework_name == "ISO 27001"
    assert ctl.mapped_frameworks == ["SOC 2"]
    assert ctl.mapping_count == 3


@pytest.mark.asyncio
async def test_get_unified_controls_unknown_owning_framework(
    service, mock_session
):
    """A clause whose framework is absent reports framework 'Unknown'."""
    clause = _make_clause(depth=1, framework_id=uuid.uuid4())

    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([clause]),
            _mock_execute_result([]),            # no frameworks
            _mock_rows_result([]),
            _mock_rows_result([]),
            _mock_execute_result([]),            # no mappings
        ]
    )

    controls = await service.get_unified_controls()

    assert controls[0].framework_name == "Unknown"
    assert controls[0].mapped_frameworks == []
    assert controls[0].mapping_count == 0


@pytest.mark.asyncio
async def test_get_unified_controls_empty(service, mock_session):
    """No clauses means no controls and no per-clause queries."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([]),
            _mock_execute_result([]),
            _mock_rows_result([]),
            _mock_rows_result([]),
        ]
    )

    controls = await service.get_unified_controls()

    assert controls == []
    assert mock_session.execute.await_count == 4
