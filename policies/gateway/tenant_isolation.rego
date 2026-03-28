package velora.gateway

default allow = false

# Allow health endpoints without auth
allow {
    startswith(input.path, "/health")
}

# Allow readiness/liveness probes
allow {
    startswith(input.path, "/ready")
}

# Allow auth endpoints (login, register, SSO) — unauthenticated by design
allow {
    startswith(input.path, "/auth/login")
}

allow {
    startswith(input.path, "/auth/register")
}

allow {
    startswith(input.path, "/auth/sso")
}

allow {
    startswith(input.path, "/auth/refresh")
}

# For all other endpoints: require valid tenant context and authenticated token
allow {
    input.tenant_id != ""
    input.token_valid == true
}
