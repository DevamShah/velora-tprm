package velora.services.vendor

default allow = false

# ---- Read access ----
read_roles := ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "Vendor Manager", "IT Security", "Viewer", "Auditor"]

allow {
    input.action == "read"
    input.roles[_] == read_roles[_]
}

# ---- Write access (create/update) ----
write_roles := ["Admin", "TPRM Manager", "Vendor Manager"]

allow {
    input.action == "write"
    input.roles[_] == write_roles[_]
}

# ---- Delete access ----
allow {
    input.action == "delete"
    input.roles[_] == "Admin"
}
