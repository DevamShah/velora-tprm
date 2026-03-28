package velora.services.scoring

default allow = false

# ---- Read access (view scores and risk ratings) ----
read_roles := ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "IT Security", "Viewer", "Auditor"]

allow {
    input.action == "read"
    input.roles[_] == read_roles[_]
}

# ---- Write access (trigger scoring, adjust weights) ----
write_roles := ["Admin", "TPRM Manager", "Risk Analyst"]

allow {
    input.action == "write"
    input.roles[_] == write_roles[_]
}

# ---- Configure access (scoring models, thresholds) ----
configure_roles := ["Admin", "TPRM Manager"]

allow {
    input.action == "configure"
    input.roles[_] == configure_roles[_]
}

# ---- Override access (manual score overrides) ----
allow {
    input.action == "override"
    input.roles[_] == "Admin"
}
