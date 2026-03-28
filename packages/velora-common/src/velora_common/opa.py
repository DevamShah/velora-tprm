"""
OPA (Open Policy Agent) client for policy evaluation.

Queries the OPA sidecar (or centralized instance) for authorization decisions.
Falls back to configurable default in development if OPA is not available.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from velora_common.logging import get_logger

logger = get_logger(__name__)

# When OPA is unreachable, this controls fail-open vs fail-closed behavior.
# In production, set VELORA_OPA_FAIL_OPEN=false to enforce fail-closed.
_FAIL_OPEN = os.environ.get("VELORA_OPA_FAIL_OPEN", "true").lower() in ("true", "1", "yes")


class OPAClient:
    """Client for querying OPA policy decisions."""

    def __init__(self, opa_url: str = "http://localhost:8181") -> None:
        self._opa_url = opa_url
        self._timeout = 2.0

    async def check(
        self,
        policy_path: str,
        input_data: dict[str, Any],
    ) -> bool:
        """
        Query OPA for a policy decision.

        Args:
            policy_path: OPA data path, e.g. "velora/gateway" or "velora/services/vendor".
                         The "/v1/data/" prefix is added automatically.
            input_data: The input document for OPA evaluation.

        Returns:
            True if the policy allows the request, False otherwise.
        """
        url = f"{self._opa_url}/v1/data/{policy_path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    url,
                    json={"input": input_data},
                )
                if response.status_code == 200:
                    result = response.json()
                    allowed = result.get("result", {}).get("allow", False)
                    logger.debug(
                        "opa_check",
                        policy=policy_path,
                        result="allow" if allowed else "deny",
                    )
                    return allowed

                logger.warning(
                    "opa_check_non_200",
                    policy=policy_path,
                    status=response.status_code,
                    body=response.text[:200],
                )
                return False

        except httpx.ConnectError:
            logger.warning(
                "opa_unreachable",
                policy=policy_path,
                fail_open=_FAIL_OPEN,
            )
            return _FAIL_OPEN

        except Exception as exc:
            logger.error(
                "opa_check_error",
                policy=policy_path,
                error=str(exc),
                fail_open=_FAIL_OPEN,
            )
            return _FAIL_OPEN

    async def check_gateway(
        self,
        path: str,
        tenant_id: str,
        roles: list[str],
        token_valid: bool,
    ) -> bool:
        """Evaluate the gateway tenant-isolation + route-access policies."""
        # First check tenant isolation
        tenant_allowed = await self.check("velora/gateway", {
            "path": path,
            "tenant_id": tenant_id,
            "token_valid": token_valid,
        })
        if not tenant_allowed:
            return False

        # Then check route-level RBAC
        return await self.check("velora/gateway/routes", {
            "path": path,
            "roles": roles,
        })

    async def check_service(
        self,
        service: str,
        action: str,
        roles: list[str],
        **kwargs: Any,
    ) -> bool:
        """Evaluate a service-level policy (e.g. vendor, assessment, evidence)."""
        return await self.check(f"velora/services/{service}", {
            "action": action,
            "roles": roles,
            **kwargs,
        })

    async def check_data_classification(
        self,
        classification: str,
        roles: list[str],
    ) -> bool:
        """Evaluate data classification access policy."""
        return await self.check("velora/services/classification", {
            "data_classification": classification,
            "roles": roles,
        })

    async def close(self) -> None:
        """Close any underlying HTTP connections."""
        pass
