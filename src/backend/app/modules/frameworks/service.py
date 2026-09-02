"""
Framework business logic — listing, clause trees, cross-mappings,
and unified control library.

Frameworks are global reference data (not tenant-scoped).
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.modules.frameworks.models import (
    ControlMapping,
    Framework,
    FrameworkClause,
)
from app.modules.frameworks.schemas import (
    ClauseTreeNode,
    FrameworkDetailResponse,
    FrameworkListResponse,
    FrameworkResponse,
    MappingResponse,
    UnifiedControl,
)

logger = get_logger(__name__)


class FrameworkService:
    """Stateless framework service — read-only global data."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- List Frameworks -------------------------------------------

    async def list_frameworks(
        self,
    ) -> FrameworkListResponse:
        """List all frameworks with clause counts."""
        query = select(Framework).order_by(
            Framework.name.asc()
        )
        result = await self._session.execute(query)
        frameworks = result.scalars().all()

        items = [
            FrameworkResponse(
                id=fw.id,
                name=fw.name,
                version=fw.version,
                description=fw.description,
                framework_type=fw.framework_type,
                source_url=fw.source_url,
                clause_count=fw.clause_count,
                status=fw.status,
                created_at=fw.created_at,
                updated_at=fw.updated_at,
            )
            for fw in frameworks
        ]
        return FrameworkListResponse(
            items=items, total=len(items)
        )

    # -- Get Framework Detail --------------------------------------

    async def get_framework(
        self, framework_id: uuid.UUID
    ) -> FrameworkDetailResponse | None:
        """Fetch framework with hierarchical clause tree."""
        query = select(Framework).where(
            Framework.id == framework_id
        )
        result = await self._session.execute(query)
        fw = result.scalars().first()
        if fw is None:
            return None

        tree = await self.get_clause_tree(framework_id)

        return FrameworkDetailResponse(
            id=fw.id,
            name=fw.name,
            version=fw.version,
            description=fw.description,
            framework_type=fw.framework_type,
            source_url=fw.source_url,
            clause_count=fw.clause_count,
            status=fw.status,
            structure=fw.structure,
            clauses=tree,
            created_at=fw.created_at,
            updated_at=fw.updated_at,
        )

    # -- Clause Tree -----------------------------------------------

    async def get_clause_tree(
        self, framework_id: uuid.UUID
    ) -> list[ClauseTreeNode]:
        """Build hierarchical clause structure."""
        query = (
            select(FrameworkClause)
            .where(
                FrameworkClause.framework_id
                == framework_id
            )
            .order_by(FrameworkClause.order_index.asc())
        )
        result = await self._session.execute(query)
        clauses = result.scalars().all()

        return self._build_tree(clauses)

    # -- Clause Mappings -------------------------------------------

    async def get_clause_mappings(
        self, clause_id: uuid.UUID
    ) -> list[MappingResponse]:
        """Get cross-framework mappings for a clause."""
        query = select(ControlMapping).where(
            (ControlMapping.source_clause_id == clause_id)
            | (
                ControlMapping.target_clause_id
                == clause_id
            )
        )
        result = await self._session.execute(query)
        mappings = result.scalars().all()

        responses = []
        for m in mappings:
            resp = await self._enrich_mapping(m)
            responses.append(resp)
        return responses

    # -- Unified Controls ------------------------------------------

    async def get_unified_controls(
        self,
    ) -> list[UnifiedControl]:
        """Deduplicated controls across all frameworks."""
        query = (
            select(FrameworkClause)
            .where(FrameworkClause.depth > 0)
            .order_by(
                FrameworkClause.framework_id,
                FrameworkClause.order_index,
            )
        )
        result = await self._session.execute(query)
        clauses = result.scalars().all()

        # Build framework name lookup
        fw_query = select(Framework)
        fw_result = await self._session.execute(fw_query)
        fw_map: dict[uuid.UUID, str] = {
            fw.id: fw.name
            for fw in fw_result.scalars().all()
        }

        # Count mappings per clause
        mapping_counts = await self._get_mapping_counts()

        controls: list[UnifiedControl] = []
        for clause in clauses:
            mapped = await self._get_mapped_frameworks(
                clause.id, fw_map
            )
            controls.append(
                UnifiedControl(
                    control_id=clause.id,
                    clause_number=clause.clause_number,
                    title=clause.title,
                    description=clause.description,
                    domain_tags=clause.domain_tags,
                    framework_name=fw_map.get(
                        clause.framework_id, "Unknown"
                    ),
                    mapped_frameworks=mapped,
                    mapping_count=mapping_counts.get(
                        clause.id, 0
                    ),
                )
            )
        return controls

    # -- Private helpers -------------------------------------------

    @staticmethod
    def _build_tree(
        clauses: list,
    ) -> list[ClauseTreeNode]:
        """Convert flat clause list into nested tree."""
        node_map: dict[uuid.UUID, ClauseTreeNode] = {}
        roots: list[ClauseTreeNode] = []

        for c in clauses:
            node = ClauseTreeNode(
                id=c.id,
                clause_number=c.clause_number,
                title=c.title,
                description=c.description,
                domain_tags=c.domain_tags,
                depth=c.depth,
                order_index=c.order_index,
                children=[],
            )
            node_map[c.id] = node

        for c in clauses:
            node = node_map[c.id]
            if (
                c.parent_clause_id
                and c.parent_clause_id in node_map
            ):
                node_map[c.parent_clause_id].children.append(
                    node
                )
            else:
                roots.append(node)

        return roots

    async def _enrich_mapping(
        self, mapping: ControlMapping
    ) -> MappingResponse:
        """Add clause/framework names to a mapping."""
        src = await self._get_clause_with_fw(
            mapping.source_clause_id
        )
        tgt = await self._get_clause_with_fw(
            mapping.target_clause_id
        )

        return MappingResponse(
            id=mapping.id,
            source_clause_id=mapping.source_clause_id,
            target_clause_id=mapping.target_clause_id,
            mapping_type=mapping.mapping_type,
            confidence=mapping.confidence,
            source_type=mapping.source_type,
            verified=mapping.verified,
            source_clause_number=src[0] if src else None,
            source_clause_title=src[1] if src else None,
            source_framework_name=src[2] if src else None,
            target_clause_number=tgt[0] if tgt else None,
            target_clause_title=tgt[1] if tgt else None,
            target_framework_name=tgt[2] if tgt else None,
            created_at=mapping.created_at,
            updated_at=mapping.updated_at,
        )

    async def _get_clause_with_fw(
        self, clause_id: uuid.UUID
    ) -> tuple | None:
        """Return (clause_number, title, framework_name)."""
        query = select(FrameworkClause).where(
            FrameworkClause.id == clause_id
        )
        result = await self._session.execute(query)
        clause = result.scalars().first()
        if clause is None:
            return None

        fw_q = select(Framework.name).where(
            Framework.id == clause.framework_id
        )
        fw_result = await self._session.execute(fw_q)
        fw_name = fw_result.scalar() or "Unknown"

        return (
            clause.clause_number,
            clause.title,
            fw_name,
        )

    async def _get_mapping_counts(
        self,
    ) -> dict[uuid.UUID, int]:
        """Count total mappings per clause (source + target)."""
        src_q = select(
            ControlMapping.source_clause_id,
            func.count().label("cnt"),
        ).group_by(ControlMapping.source_clause_id)
        tgt_q = select(
            ControlMapping.target_clause_id,
            func.count().label("cnt"),
        ).group_by(ControlMapping.target_clause_id)

        src_result = await self._session.execute(src_q)
        tgt_result = await self._session.execute(tgt_q)

        counts: dict[uuid.UUID, int] = {}
        for row in src_result:
            counts[row[0]] = counts.get(row[0], 0) + row[1]
        for row in tgt_result:
            counts[row[0]] = counts.get(row[0], 0) + row[1]
        return counts

    async def _get_mapped_frameworks(
        self,
        clause_id: uuid.UUID,
        fw_map: dict[uuid.UUID, str],
    ) -> list[str]:
        """Get framework names this clause maps to."""
        query = select(ControlMapping).where(
            (ControlMapping.source_clause_id == clause_id)
            | (
                ControlMapping.target_clause_id
                == clause_id
            )
        )
        result = await self._session.execute(query)
        mappings = result.scalars().all()

        fw_ids: set = set()
        for m in mappings:
            other_id = (
                m.target_clause_id
                if m.source_clause_id == clause_id
                else m.source_clause_id
            )
            clause_q = select(
                FrameworkClause.framework_id
            ).where(FrameworkClause.id == other_id)
            clause_r = await self._session.execute(
                clause_q
            )
            fid = clause_r.scalar()
            if fid:
                fw_ids.add(fid)

        return [
            fw_map.get(fid, "Unknown") for fid in fw_ids
        ]
