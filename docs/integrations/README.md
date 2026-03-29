# Velora TPRM -- Integration Guides

**Version:** 1.0.0
**Last Updated:** 2026-03-29

This directory contains step-by-step integration guides for connecting third-party services to Velora TPRM.

---

## SSO (Single Sign-On) Integrations

| Provider | Protocol | Guide |
|---|---|---|
| Okta | OIDC / SAML 2.0 | [sso-okta.md](sso-okta.md) |
| Microsoft Entra ID (Azure AD) | OIDC | [sso-azure-ad.md](sso-azure-ad.md) |
| Google Workspace | OIDC | [sso-google-workspace.md](sso-google-workspace.md) |

### What Each Guide Covers

- Prerequisites and required access levels
- Step-by-step provider configuration (with UI navigation paths)
- Velora TPRM configuration (Admin > Integrations > SSO)
- Group-to-role mapping
- Just-In-Time (JIT) user provisioning
- Testing procedures
- Troubleshooting common issues
- Security considerations

### Common Configuration Path in Velora

All SSO integrations are configured at:

**Admin Settings (gear icon, bottom-left) > Integrations > SSO**

### Supported Velora Roles for Mapping

| Role | Description |
|---|---|
| Platform Administrator | Full system administration |
| Risk Manager | Manage vendor risk assessments and thresholds |
| Risk Analyst | Conduct assessments and review evidence |
| Vendor Manager | Manage vendor relationships and onboarding |
| Auditor | Read-only access to all risk data and reports |
| Viewer | Read-only access to dashboards |

---

## Additional Integrations (Planned)

| Integration | Status | Guide |
|---|---|---|
| SCIM Provisioning (Okta) | Planned | -- |
| SCIM Provisioning (Azure AD) | Documented in Azure AD guide | [sso-azure-ad.md](sso-azure-ad.md#scim-provisioning-advanced) |
| SCIM Provisioning (Google) | Planned | -- |
| GRC Platform Connectors | Planned | -- |
| Vulnerability Scanner Feeds | Planned | -- |
| Ticketing System Webhooks | Planned | -- |

---

*Maintained by the Velora TPRM platform team.*
