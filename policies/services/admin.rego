package velora.services.admin

default allow = false

# All admin actions require Admin role
allow {
    input.action == "read"
    input.roles[_] == "Admin"
}

allow {
    input.action == "write"
    input.roles[_] == "Admin"
}

allow {
    input.action == "delete"
    input.roles[_] == "Admin"
}

# Tenant configuration — Admin only
allow {
    input.action == "configure_tenant"
    input.roles[_] == "Admin"
}

# User management — Admin only
allow {
    input.action == "manage_users"
    input.roles[_] == "Admin"
}

# Role assignment — Admin only
allow {
    input.action == "assign_roles"
    input.roles[_] == "Admin"
}
