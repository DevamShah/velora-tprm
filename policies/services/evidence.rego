package velora.services.evidence

default allow = false

# ---- Read access ----
read_roles := ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "IT Security", "Auditor"]

allow {
    input.action == "read"
    input.roles[_] == read_roles[_]
}

# ---- Upload access ----
upload_roles := ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst"]

allow {
    input.action == "upload"
    input.roles[_] == upload_roles[_]
}

# ---- Write access (update metadata, link evidence) ----
write_roles := ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst"]

allow {
    input.action == "write"
    input.roles[_] == write_roles[_]
}

# ---- Delete access ----
allow {
    input.action == "delete"
    input.roles[_] == "Admin"
}
