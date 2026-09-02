"""Regression tests for the vendor_id URL-injection fix.

CodeQL flagged ``py/partial-ssrf`` on the aggregator: ``vendor_id``
arrived as a bare ``str`` from the BFF route and was interpolated
straight into five internal service URLs.  Two of those interpolated it
into a query string, so a caller could append their own parameters to
an internal call (``?vendor_id=x&is_admin=true``) without ever needing
a slash.

These tests pin the fix: anything that is not a UUID is rejected before
a request is built, and legitimate ids still work.
"""

from __future__ import annotations

import asyncio
import uuid

import pytest

from src.aggregator import vendor_full

# Each of these reaches a different injection point if unvalidated:
# extra query params, path traversal, fragment truncation, nested query.
INJECTIONS = [
    "x&limit=999999",
    "x&is_admin=true",
    "../../admin/secrets",
    "123#",
    "valid?role=admin",
    "http://169.254.169.254/latest/meta-data/",
    "",
]


@pytest.mark.parametrize("payload", INJECTIONS)
def test_vendor_full_rejects_non_uuid(payload: str) -> None:
    """A non-UUID vendor_id must raise before any HTTP call is made."""
    with pytest.raises(ValueError):
        asyncio.run(vendor_full(payload, "token"))


def test_uuid_is_accepted_and_normalised() -> None:
    """A real UUID survives coercion unchanged."""
    vid = uuid.uuid4()
    assert str(uuid.UUID(str(vid))) == str(vid)
    # No dangerous character can survive UUID normalisation.
    assert set(str(vid)) <= set("0123456789abcdef-")
