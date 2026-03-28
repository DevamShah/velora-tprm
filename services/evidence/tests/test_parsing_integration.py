"""
Tests for evidence parsing — extractors, parser client, storage.

Unit tests mock Azure and MinIO. Integration tests require real services.
"""

from __future__ import annotations

import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.doc_parser import DocumentParseResult, ParsedPage
from src.extractors import get_extractor
from src.extractors.soc2 import extract_soc2
from src.extractors.iso27001 import extract_iso27001
from src.extractors.pentest import extract_pentest
from src.storage import StorageClient


TENANT = uuid.UUID("11111111-1111-1111-1111-111111111111")
EVIDENCE = uuid.UUID("22222222-2222-2222-2222-222222222222")


def _make_parse_result(content: str) -> DocumentParseResult:
    """Helper to create a parse result from raw text."""
    return DocumentParseResult(
        pages=[ParsedPage(
            page_number=1,
            content=content,
        )],
        total_pages=1,
        content=content,
        tables=[],
        key_value_pairs=[],
        model_id="test",
    )


# -- Extractor registry tests -----------------------------------------


class TestExtractorRegistry:

    def test_soc2_extractor_registered(self):
        assert get_extractor("soc2") is not None

    def test_iso_extractor_registered(self):
        assert get_extractor("iso_cert") is not None

    def test_pentest_extractor_registered(self):
        assert get_extractor("pen_test") is not None

    def test_unknown_type_returns_none(self):
        assert get_extractor("unknown_doc") is None


# -- SOC 2 extractor tests --------------------------------------------


class TestSOC2Extractor:

    def test_extracts_audit_period(self):
        content = (
            "This report covers the period from "
            "January 1, 2025 to December 31, 2025."
        )
        result = _make_parse_result(content)
        extractions = extract_soc2(
            result, TENANT, EVIDENCE
        )
        fields = {e.field_name for e in extractions}
        assert "audit_period" in fields

    def test_extracts_opinion_unqualified(self):
        content = (
            "In our opinion, the controls were suitably "
            "designed. Unqualified opinion issued."
        )
        result = _make_parse_result(content)
        extractions = extract_soc2(
            result, TENANT, EVIDENCE
        )
        opinion = next(
            (e for e in extractions
             if e.field_name == "opinion_type"),
            None,
        )
        assert opinion is not None
        assert opinion.field_value == "Unqualified"

    def test_extracts_no_exceptions(self):
        content = "No exceptions were noted during the audit."
        result = _make_parse_result(content)
        extractions = extract_soc2(
            result, TENANT, EVIDENCE
        )
        exc = next(
            (e for e in extractions
             if e.field_name == "exceptions_noted"),
            None,
        )
        assert exc is not None
        assert exc.field_value == "None"

    def test_extracts_trust_criteria(self):
        content = (
            "The system addresses the security and "
            "availability trust service criteria."
        )
        result = _make_parse_result(content)
        extractions = extract_soc2(
            result, TENANT, EVIDENCE
        )
        tsc = next(
            (e for e in extractions
             if e.field_name == "trust_service_criteria"),
            None,
        )
        assert tsc is not None
        assert "Security" in tsc.field_value


# -- ISO 27001 extractor tests ----------------------------------------


class TestISO27001Extractor:

    def test_extracts_standard_version(self):
        content = "Certified to ISO/IEC 27001:2022"
        result = _make_parse_result(content)
        extractions = extract_iso27001(
            result, TENANT, EVIDENCE
        )
        std = next(
            (e for e in extractions
             if e.field_name == "standard"),
            None,
        )
        assert std is not None
        assert "27001:2022" in std.field_value

    def test_extracts_cert_number(self):
        content = "Certificate No: IS-2025-78432"
        result = _make_parse_result(content)
        extractions = extract_iso27001(
            result, TENANT, EVIDENCE
        )
        cert = next(
            (e for e in extractions
             if e.field_name == "certificate_number"),
            None,
        )
        assert cert is not None
        assert cert.field_value == "IS-2025-78432"


# -- Pen test extractor tests -----------------------------------------


class TestPenTestExtractor:

    def test_extracts_methodology(self):
        content = (
            "Testing was conducted following OWASP "
            "and PTES methodologies."
        )
        result = _make_parse_result(content)
        extractions = extract_pentest(
            result, TENANT, EVIDENCE
        )
        method = next(
            (e for e in extractions
             if e.field_name == "methodology"),
            None,
        )
        assert method is not None
        assert "OWASP" in method.field_value

    def test_counts_findings(self):
        content = "0 critical, 2 high, 5 medium, 3 low"
        result = _make_parse_result(content)
        extractions = extract_pentest(
            result, TENANT, EVIDENCE
        )
        names = {e.field_name for e in extractions}
        assert "critical_findings" in names
        assert "high_findings" in names
        critical = next(
            e for e in extractions
            if e.field_name == "critical_findings"
        )
        assert critical.field_value == "0"


# -- Storage tests (mock MinIO) ---------------------------------------


class TestStorage:

    @patch("src.storage.Minio")
    def test_presigned_upload_url(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_client.presigned_put_object.return_value = (
            "http://minio:9000/test/key?signed=true"
        )
        mock_minio_cls.return_value = mock_client

        storage = StorageClient()
        url = storage.get_presigned_upload_url("test/key")
        assert "minio" in url
        assert "test/key" in mock_client.presigned_put_object.call_args[0]

    @patch("src.storage.Minio")
    def test_download_bytes(self, mock_minio_cls):
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_response = MagicMock()
        mock_response.read.return_value = b"PDF content"
        mock_client.get_object.return_value = mock_response
        mock_minio_cls.return_value = mock_client

        storage = StorageClient()
        data = storage.download_bytes("test/key")
        assert data == b"PDF content"
