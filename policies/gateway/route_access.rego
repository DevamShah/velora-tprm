package velora.gateway.routes

default allow = false

# Map endpoint prefixes to the roles permitted to access them
route_roles := {
    "/vendors": ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "Vendor Manager", "IT Security", "Viewer", "Auditor"],
    "/assessments": ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "IT Security"],
    "/frameworks": ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "IT Security", "Viewer", "Auditor"],
    "/scoring": ["Admin", "TPRM Manager", "Risk Analyst"],
    "/evidence": ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst"],
    "/monitoring": ["Admin", "TPRM Manager", "Risk Analyst", "IT Security"],
    "/findings": ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst"],
    "/communications": ["Admin", "TPRM Manager"],
    "/reports": ["Admin", "TPRM Manager", "Risk Analyst", "Viewer", "Auditor"],
    "/admin": ["Admin"],
    "/ai": ["Admin", "TPRM Manager", "Risk Analyst"],
    "/workflows": ["Admin", "TPRM Manager"],
    "/dashboard": ["Admin", "TPRM Manager", "Risk Analyst", "GRC Analyst", "Vendor Manager", "IT Security", "Viewer", "Auditor"],
}

# Allow if the user has a role that matches a route prefix
allow {
    some prefix
    startswith(input.path, prefix)
    role := input.roles[_]
    allowed := route_roles[prefix][_]
    role == allowed
}
