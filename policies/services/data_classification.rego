package velora.services.classification

default allow = false

# Restricted data — only Admin and IT Security
allow {
    input.data_classification == "restricted"
    input.roles[_] == "Admin"
}

allow {
    input.data_classification == "restricted"
    input.roles[_] == "IT Security"
}

# Confidential — Admin, TPRM Manager, Risk Analyst, IT Security
confidential_roles := ["Admin", "TPRM Manager", "Risk Analyst", "IT Security"]

allow {
    input.data_classification == "confidential"
    input.roles[_] == confidential_roles[_]
}

# Internal — all authenticated users
allow {
    input.data_classification == "internal"
}

# Public — all authenticated users
allow {
    input.data_classification == "public"
}
