"""
Typed extraction pipelines for different document types.

Each extractor takes a DocumentParseResult and returns structured
EvidenceExtraction rows specific to that document type.
"""

from .soc2 import extract_soc2
from .iso27001 import extract_iso27001
from .pentest import extract_pentest

EXTRACTOR_MAP = {
    "soc2": extract_soc2,
    "iso_cert": extract_iso27001,
    "pen_test": extract_pentest,
}


def get_extractor(document_type: str):
    """Get the extraction function for a document type."""
    return EXTRACTOR_MAP.get(document_type)
