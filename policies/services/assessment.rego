package velora.services.assessment

default allow = false

# ---- Read access ----
read_roles := ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "IT Security", "Viewer", "Auditor"]

allow {
    input.action == "read"
    input.roles[_] == read_roles[_]
}

# ---- Write access (create/update assessments) ----
write_roles := ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst"]

allow {
    input.action == "write"
    input.roles[_] == write_roles[_]
}

# ---- Submit access (submit completed assessments) ----
submit_roles := ["Admin", "TPRM Manager", "Risk Analyst"]

allow {
    input.action == "submit"
    input.roles[_] == submit_roles[_]
}

# ---- Delete access ----
allow {
    input.action == "delete"
    input.roles[_] == "Admin"
}
