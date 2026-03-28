"""
Async wrapper around Azure Document Intelligence for evidence parsing.

Handles long-running document analysis with polling, timeout, and retry.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from velora_common.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_TIMEOUT = 300  # 5 minutes for large documents
_MAX_RETRIES = 3


@dataclass
class ParsedPage:
    """Single page extraction result."""

    page_number: int
    content: str
    tables: List[Dict[str, Any]] = field(
        default_factory=list
    )
    key_value_pairs: List[Dict[str, str]] = field(
        default_factory=list
    )


@dataclass
class DocumentParseResult:
    """Complete document parse output."""

    pages: List[ParsedPage]
    total_pages: int
    content: str
    tables: List[Dict[str, Any]]
    key_value_pairs: List[Dict[str, str]]
    model_id: str


class DocumentParser:
    """Async Azure Document Intelligence client."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self._endpoint = endpoint or os.environ.get(
            "AZURE_DOC_INTELLIGENCE_ENDPOINT", ""
        )
        self._api_key = api_key or os.environ.get(
            "AZURE_DOC_INTELLIGENCE_KEY", ""
        )
        self._client = None

        if not self._endpoint or not self._api_key:
            logger.warning(
                "doc_parser_not_configured",
                reason="Azure credentials not set",
            )

    def _get_client(self):
        """Lazy-initialize the Azure client."""
        if self._client is None:
            from azure.ai.documentintelligence import (
                DocumentIntelligenceClient,
            )
            from azure.core.credentials import (
                AzureKeyCredential,
            )

            self._client = DocumentIntelligenceClient(
                endpoint=self._endpoint,
                credential=AzureKeyCredential(
                    self._api_key
                ),
            )
        return self._client

    @retry(
        stop=stop_after_attempt(_MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        reraise=True,
    )
    async def parse_document(
        self,
        file_bytes: bytes,
        content_type: str = "application/pdf",
    ) -> DocumentParseResult:
        """Parse a document using Azure prebuilt-layout model.

        Azure SDK is synchronous — calls are wrapped in
        asyncio.to_thread() to avoid blocking the event loop.
        """
        if not self._endpoint or not self._api_key:
            raise ValueError(
                "Azure Document Intelligence not configured"
            )

        logger.info(
            "doc_parse_started",
            content_type=content_type,
            size_bytes=len(file_bytes),
        )

        try:
            result = await asyncio.to_thread(
                self._sync_parse, file_bytes, content_type
            )
        except Exception as exc:
            logger.error(
                "doc_parse_failed",
                error_type=type(exc).__name__,
            )
            raise

        pages = []
        for page in (result.pages or []):
            page_content = ""
            for line in (page.lines or []):
                page_content += line.content + "\n"

            kvps = []
            tables_on_page = []

            pages.append(ParsedPage(
                page_number=page.page_number,
                content=page_content,
                tables=tables_on_page,
                key_value_pairs=kvps,
            ))

        # Extract global key-value pairs
        all_kvps = []
        for kvp in (result.key_value_pairs or []):
            key = kvp.key.content if kvp.key else ""
            value = (
                kvp.value.content if kvp.value else ""
            )
            all_kvps.append({"key": key, "value": value})

        # Extract global tables
        all_tables = []
        for table in (result.tables or []):
            cells = []
            for cell in (table.cells or []):
                cells.append({
                    "row": cell.row_index,
                    "col": cell.column_index,
                    "content": cell.content,
                })
            all_tables.append({
                "row_count": table.row_count,
                "col_count": table.column_count,
                "cells": cells,
            })

        full_content = result.content or ""

        logger.info(
            "doc_parse_complete",
            total_pages=len(pages),
            kvps_found=len(all_kvps),
            tables_found=len(all_tables),
        )

        return DocumentParseResult(
            pages=pages,
            total_pages=len(pages),
            content=full_content,
            tables=all_tables,
            key_value_pairs=all_kvps,
            model_id="prebuilt-layout",
        )

    def _sync_parse(
        self, file_bytes: bytes, content_type: str
    ):
        """Synchronous Azure parse — runs in thread."""
        client = self._get_client()
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            analyze_request=file_bytes,
            content_type=content_type,
        )
        return poller.result()

    def close(self) -> None:
        """Close the underlying client."""
        if self._client is not None:
            self._client.close()
            self._client = None
