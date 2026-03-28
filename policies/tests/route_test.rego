package velora.gateway.routes_test

import data.velora.gateway.routes

# Admin can access /vendors
test_admin_vendors_allowed {
    routes.allow with input as {"path": "/vendors", "roles": ["Admin"]}
}

# Viewer can access /vendors (read-only role but route-level access)
test_viewer_vendors_allowed {
    routes.allow with input as {"path": "/vendors", "roles": ["Viewer"]}
}

# Risk Analyst can access /assessments
test_risk_analyst_assessments_allowed {
    routes.allow with input as {"path": "/assessments/123", "roles": ["Risk Analyst"]}
}

# Viewer cannot access /assessments
test_viewer_assessments_denied {
    not routes.allow with input as {"path": "/assessments", "roles": ["Viewer"]}
}

# Only Admin can access /admin
test_admin_admin_allowed {
    routes.allow with input as {"path": "/admin/settings", "roles": ["Admin"]}
}

# TPRM Manager cannot access /admin
test_tprm_manager_admin_denied {
    not routes.allow with input as {"path": "/admin", "roles": ["TPRM Manager"]}
}

# Auditor can access /reports
test_auditor_reports_allowed {
    routes.allow with input as {"path": "/reports/quarterly", "roles": ["Auditor"]}
}

# Auditor cannot access /scoring
test_auditor_scoring_denied {
    not routes.allow with input as {"path": "/scoring", "roles": ["Auditor"]}
}

# User with multiple roles gets combined access
test_multi_role_access {
    routes.allow with input as {"path": "/admin", "roles": ["Risk Analyst", "Admin"]}
}

# Vendor Manager can access /vendors but not /assessments
test_vendor_manager_vendors_allowed {
    routes.allow with input as {"path": "/vendors", "roles": ["Vendor Manager"]}
}

test_vendor_manager_assessments_denied {
    not routes.allow with input as {"path": "/assessments", "roles": ["Vendor Manager"]}
}

# Unknown path should be denied
test_unknown_path_denied {
    not routes.allow with input as {"path": "/unknown", "roles": ["Admin"]}
}
