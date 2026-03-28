package velora.gateway_test

import data.velora.gateway

# Health endpoint should be accessible without auth
test_health_allowed {
    gateway.allow with input as {"path": "/health", "tenant_id": "", "token_valid": false}
}

# Readiness probe should be accessible without auth
test_ready_allowed {
    gateway.allow with input as {"path": "/ready", "tenant_id": "", "token_valid": false}
}

# Auth login endpoint should be accessible without tenant
test_auth_login_allowed {
    gateway.allow with input as {"path": "/auth/login", "tenant_id": "", "token_valid": false}
}

# Auth register endpoint should be accessible without tenant
test_auth_register_allowed {
    gateway.allow with input as {"path": "/auth/register", "tenant_id": "", "token_valid": false}
}

# Auth SSO endpoint should be accessible without tenant
test_auth_sso_allowed {
    gateway.allow with input as {"path": "/auth/sso/callback", "tenant_id": "", "token_valid": false}
}

# Auth refresh endpoint should be accessible without tenant
test_auth_refresh_allowed {
    gateway.allow with input as {"path": "/auth/refresh", "tenant_id": "", "token_valid": false}
}

# Request with no tenant and no token should be denied
test_no_tenant_denied {
    not gateway.allow with input as {"path": "/vendors", "tenant_id": "", "token_valid": true}
}

# Request with tenant but invalid token should be denied
test_invalid_token_denied {
    not gateway.allow with input as {"path": "/vendors", "tenant_id": "t-001", "token_valid": false}
}

# Valid request with tenant and token should be allowed
test_valid_tenant_allowed {
    gateway.allow with input as {"path": "/vendors", "tenant_id": "t-001", "token_valid": true}
}

# Completely empty input should be denied
test_empty_input_denied {
    not gateway.allow with input as {"path": "/vendors", "tenant_id": "", "token_valid": false}
}
