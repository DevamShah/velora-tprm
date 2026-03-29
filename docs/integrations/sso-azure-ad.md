# Velora TPRM -- Microsoft Entra ID (Azure AD) SSO Integration Guide

**Version:** 1.0.0
**Last Updated:** 2026-03-29
**Applies To:** Velora TPRM v2.1.0+
**Protocol:** OIDC (OpenID Connect)

> **Note:** Microsoft rebranded Azure Active Directory to Microsoft Entra ID in 2023. This guide uses both names interchangeably. All Azure Portal paths remain the same.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [App Registration in Azure Portal](#2-app-registration-in-azure-portal)
3. [Enterprise Application Setup](#3-enterprise-application-setup)
4. [Configure SSO in Velora TPRM](#4-configure-sso-in-velora-tprm)
5. [Group Claims for Role Mapping](#5-group-claims-for-role-mapping)
6. [Just-In-Time (JIT) User Provisioning](#6-just-in-time-jit-user-provisioning)
7. [Conditional Access Policies](#7-conditional-access-policies)
8. [Testing the SSO Connection](#8-testing-the-sso-connection)
9. [Troubleshooting](#9-troubleshooting)
10. [Security Considerations](#10-security-considerations)

---

## 1. Prerequisites

| Requirement | Detail |
|---|---|
| Azure AD tenant | An active Microsoft Entra ID (Azure AD) tenant |
| Azure role | `Application Administrator`, `Cloud Application Administrator`, or `Global Administrator` role in Azure AD |
| Velora TPRM instance | Running v2.1.0 or later, accessible via HTTPS |
| Custom domain | A verified domain for Velora (e.g., `tprm.yourcompany.com`) |
| TLS certificate | Valid TLS certificate on your Velora domain |
| Velora admin access | An account with `Platform Administrator` role in Velora TPRM |
| Azure AD groups | Pre-created security groups for Velora role mapping (see Section 5) |
| Azure AD P1/P2 license | Required for Conditional Access policies (Section 7) and group claims in tokens |

---

## 2. App Registration in Azure Portal

### Step 1: Open Azure Portal

1. Navigate to `https://portal.azure.com`.
2. Sign in with an account that has Application Administrator (or higher) privileges.

### Step 2: Navigate to App Registrations

1. In the top search bar, type **App registrations** and select it from the results.
   - Alternatively: Left sidebar > **Azure Active Directory** > **App registrations**.
2. Click **+ New registration** at the top of the page.

### Step 3: Register the Application

Fill in the registration form:

| Field | Value |
|---|---|
| **Name** | `Velora TPRM` |
| **Supported account types** | **Accounts in this organizational directory only** (Single tenant) -- select this for most enterprise deployments. Choose "Multitenant" only if Velora serves multiple Azure AD tenants. |
| **Redirect URI (optional)** | Platform: **Web**. URI: `https://{your-domain}/auth/callback/azure` |

Click **Register**.

### Step 4: Collect Application Identifiers

After registration, Azure redirects you to the app's **Overview** page. Record these values:

| Field | Where to Find | Example |
|---|---|---|
| **Application (client) ID** | Overview page, top section | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| **Directory (tenant) ID** | Overview page, top section | `f0e1d2c3-b4a5-6789-0fed-cba987654321` |

### Step 5: Create a Client Secret

1. In the left sidebar of the app registration, click **Certificates & secrets**.
2. Click the **Client secrets** tab.
3. Click **+ New client secret**.
4. Fill in:
   - **Description:** `Velora TPRM Production`
   - **Expires:** Select a duration. Recommended: **24 months** (set a calendar reminder to rotate before expiry).
5. Click **Add**.
6. **Immediately copy the secret Value** (not the Secret ID). This is shown only once. If you navigate away without copying, you must create a new secret.

### Step 6: Configure API Permissions

1. In the left sidebar, click **API permissions**.
2. Click **+ Add a permission**.
3. Select **Microsoft Graph**.
4. Select **Delegated permissions**.
5. Search for and add the following permissions:

| Permission | Purpose |
|---|---|
| `openid` | Required for OIDC |
| `profile` | Access user's name and basic profile |
| `email` | Access user's email address |
| `User.Read` | Read the signed-in user's basic profile |
| `GroupMember.Read.All` | Read group memberships for role mapping |

6. Click **Add permissions**.
7. If your organization requires it, click **Grant admin consent for {your-org}** (requires Global Administrator).
   - The "Status" column should show green checkmarks after consent is granted.

### Step 7: Configure Token Claims

1. In the left sidebar, click **Token configuration**.
2. Click **+ Add optional claim**.
3. Select **ID** token type.
4. Check the following claims:
   - `email`
   - `family_name`
   - `given_name`
   - `preferred_username`
5. Click **Add**. If prompted to add Microsoft Graph permissions, click **Yes**.

### Step 8: Construct OIDC Endpoints

Using your Tenant ID, construct these URLs:

| URL Type | Value |
|---|---|
| **Issuer URI** | `https://login.microsoftonline.com/{tenant-id}/v2.0` |
| **Authorization Endpoint** | `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize` |
| **Token Endpoint** | `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token` |
| **UserInfo Endpoint** | `https://graph.microsoft.com/oidc/userinfo` |
| **JWKS URI** | `https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys` |
| **OpenID Configuration** | `https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration` |

Replace `{tenant-id}` with your Directory (tenant) ID from Step 4.

---

## 3. Enterprise Application Setup

The App Registration creates an Enterprise Application automatically. You need to configure user assignment and additional settings here.

### Step 1: Navigate to Enterprise Applications

1. In Azure Portal, search for **Enterprise applications**.
2. Find **Velora TPRM** in the list (or search by name).
3. Click on it.

### Step 2: Require User Assignment

1. In the left sidebar, click **Properties**.
2. Set **Assignment required?** to **Yes**.
   - When set to Yes, only users or groups explicitly assigned to the application can sign in.
   - When set to No, all users in the tenant can sign in.
3. Click **Save**.

### Step 3: Assign Users and Groups

1. In the left sidebar, click **Users and groups**.
2. Click **+ Add user/group**.
3. Under **Users and groups**, click **None Selected**.
4. Search for and select the Azure AD security groups that should have Velora access:
   - `velora-platform-admins`
   - `velora-risk-managers`
   - `velora-analysts`
   - `velora-vendor-managers`
   - `velora-auditors`
   - `velora-viewers`
5. Click **Select**, then **Assign**.

### Step 4: Configure App Roles (Optional Advanced Setup)

If you prefer Azure AD App Roles over group claims:

1. Go back to **App registrations** > **Velora TPRM**.
2. In the left sidebar, click **App roles**.
3. Click **+ Create app role** for each Velora role:

| Display name | Value | Description | Allowed member types |
|---|---|---|---|
| Platform Administrator | `platform_admin` | Full system access | Users/Groups |
| Risk Manager | `risk_manager` | Risk assessment management | Users/Groups |
| Risk Analyst | `analyst` | Assessment execution | Users/Groups |
| Vendor Manager | `vendor_manager` | Vendor lifecycle management | Users/Groups |
| Auditor | `auditor` | Read-only audit access | Users/Groups |
| Viewer | `viewer` | Dashboard view only | Users/Groups |

4. Then assign these roles to groups in the Enterprise Application's **Users and groups** section.

---

## 4. Configure SSO in Velora TPRM

### Step 1: Navigate to SSO Settings

1. Log into Velora TPRM with a Platform Administrator account.
2. Click the **gear icon** in the bottom-left of the sidebar to open **Admin Settings**.
3. Navigate to **Integrations** > **SSO**.

### Step 2: Select Identity Provider

1. Click **Add SSO Provider**.
2. Select **Microsoft Entra ID (Azure AD)** from the provider list.

### Step 3: Enter Configuration

| Velora Field | Value |
|---|---|
| **Protocol** | OIDC |
| **Client ID** | Application (client) ID from Section 2, Step 4 |
| **Client Secret** | Client secret value from Section 2, Step 5 |
| **Tenant ID** | Directory (tenant) ID from Section 2, Step 4 |
| **Issuer URL** | `https://login.microsoftonline.com/{tenant-id}/v2.0` |
| **Redirect URI** | `https://{your-domain}/auth/callback/azure` (auto-populated) |
| **Scopes** | `openid profile email User.Read GroupMember.Read.All` |
| **Groups Claim Name** | `groups` (or `roles` if using App Roles) |

### Step 4: Save and Verify

1. Click **Save Configuration**.
2. Velora performs a metadata validation check against the OpenID Configuration endpoint.
3. If validation passes, the status indicator turns green.

---

## 5. Group Claims for Role Mapping

### Understanding Azure AD Group Claims

Azure AD can include group membership in the ID token. There are two approaches:

**Approach A: Security Group Object IDs (Default)**

Azure AD includes group Object IDs (GUIDs) in the `groups` claim. You map these GUIDs to Velora roles.

**Approach B: App Roles**

Azure AD includes role values in the `roles` claim. This is cleaner but requires more setup (Section 3, Step 4).

### Configuring Group Claims (Approach A)

#### In Azure Portal:

1. Go to **App registrations** > **Velora TPRM** > **Token configuration**.
2. Click **+ Add groups claim**.
3. Select **Security groups** (or **All groups** if you use Microsoft 365 groups).
4. Under **Customize token properties by type**:
   - For **ID** tokens: Select **Group ID** (this emits Object IDs).
5. Click **Add**.

#### Finding Group Object IDs:

1. In Azure Portal, go to **Azure Active Directory** > **Groups**.
2. Search for each Velora group.
3. Click on the group. The **Object Id** is displayed on the Overview page.
4. Record each Object ID.

### Configuring Role Mapping in Velora

1. In Velora Admin, go to **Integrations** > **SSO** > **Role Mapping** tab.
2. Map each Azure AD group to a Velora role:

| Azure AD Group (Object ID or App Role Value) | Velora Role |
|---|---|
| `a1b2c3d4-...` (velora-platform-admins) | Platform Administrator |
| `e5f6a7b8-...` (velora-risk-managers) | Risk Manager |
| `c9d0e1f2-...` (velora-analysts) | Risk Analyst |
| `34a5b6c7-...` (velora-vendor-managers) | Vendor Manager |
| `d8e9f0a1-...` (velora-auditors) | Auditor |
| `b2c3d4e5-...` (velora-viewers) | Viewer |

3. Set a **Default Role** for unmapped users (recommended: `Viewer`).
4. Configure **Multi-Group Behavior** (Highest privilege wins / First match / Deny).
5. Click **Save**.

### Group Overage Handling

Azure AD has a limit of 200 groups in a token. If a user belongs to more than 200 groups:

- Azure AD omits the `groups` claim and includes a `_claim_names` and `_claim_sources` reference instead.
- Velora automatically detects this and calls the Microsoft Graph API to retrieve the full group list.
- This requires the `GroupMember.Read.All` permission (configured in Section 2, Step 6).

---

## 6. Just-In-Time (JIT) User Provisioning

### Step 1: Enable JIT Provisioning

1. In Velora Admin, go to **Integrations** > **SSO** > **Provisioning** tab.
2. Toggle **Enable JIT Provisioning** to ON.

### Step 2: Configure JIT Settings

| Setting | Recommended Value | Description |
|---|---|---|
| **Auto-create users** | Enabled | Create Velora accounts on first SSO login |
| **Default role for JIT users** | Viewer | Assigned when no group mapping matches |
| **Update profile on login** | Enabled | Sync name/email changes from Azure AD |
| **Update group membership on login** | Enabled | Re-evaluate role on each login |
| **Deactivate on group removal** | Enabled | Deactivate if removed from all mapped groups |
| **Allowed email domains** | `yourcompany.com` | Restrict provisioning to verified domains |

### Step 3: Save

Click **Save Provisioning Settings**.

### SCIM Provisioning (Advanced)

For organizations that need proactive provisioning (create/update/deactivate users without requiring login), Velora supports SCIM 2.0:

1. In Velora Admin, go to **Integrations** > **SSO** > **SCIM** tab.
2. Copy the **SCIM Endpoint URL** and **Bearer Token**.
3. In Azure Portal, go to **Enterprise applications** > **Velora TPRM** > **Provisioning**.
4. Set **Provisioning Mode** to **Automatic**.
5. Enter:
   - **Tenant URL:** The Velora SCIM endpoint.
   - **Secret Token:** The Velora SCIM bearer token.
6. Click **Test Connection**, then **Save**.
7. Under **Mappings**, configure attribute mappings for users and groups.
8. Set the **Provisioning Status** to **On**.

---

## 7. Conditional Access Policies

Conditional Access policies in Azure AD add additional security controls for Velora access. These require Azure AD P1 or P2 licenses.

### Recommended Policy: Require MFA for Velora

1. In Azure Portal, go to **Azure Active Directory** > **Security** > **Conditional Access**.
2. Click **+ New policy**.
3. Configure:

| Section | Setting |
|---|---|
| **Name** | `Require MFA for Velora TPRM` |
| **Users** | Include: **All users**. Exclude: Break-glass accounts. |
| **Target resources** | Cloud apps > Select apps > **Velora TPRM** |
| **Conditions** | (Leave defaults, or add location/device conditions) |
| **Grant** | **Require multifactor authentication** |
| **Session** | Sign-in frequency: **8 hours** |

4. Set **Enable policy** to **On**.
5. Click **Create**.

### Recommended Policy: Block Untrusted Locations

1. Create a new Conditional Access policy.
2. Configure:

| Section | Setting |
|---|---|
| **Name** | `Block Velora from untrusted locations` |
| **Users** | Include: **All users** |
| **Target resources** | **Velora TPRM** |
| **Conditions** | Locations > Include: **Any location**. Exclude: **Selected locations** (your office IPs, VPN ranges). |
| **Grant** | **Block access** |

3. Enable and create.

### Recommended Policy: Require Compliant Device

1. Create a new Conditional Access policy.
2. Target Velora TPRM.
3. Under **Grant**, select **Require device to be marked as compliant** (requires Intune enrollment).

---

## 8. Testing the SSO Connection

### Step 1: Use the Built-in Test

1. In Velora Admin, go to **Integrations** > **SSO**.
2. Click **Test Connection**.
3. A new tab opens and redirects to the Microsoft login page.
4. Authenticate with your Azure AD credentials.
5. After redirect, Velora displays test results:
   - Authentication status.
   - Claims received (email, name, groups/roles).
   - Mapped Velora role.
   - Warnings or errors.

### Step 2: Test with a Non-Admin User

1. Open an incognito/private browser window.
2. Navigate to `https://{your-domain}/login`.
3. Click **Sign in with Microsoft**.
4. Authenticate with a non-admin Azure AD account assigned to the Enterprise Application.
5. Verify:
   - Correct dashboard loads.
   - Role and permissions match the expected group mapping.
   - User appears in Velora Admin > **Users** with "SSO (Azure AD)" as auth method.

### Step 3: Test Conditional Access

1. If you configured MFA policy, verify MFA is prompted during Velora login.
2. If you configured location policy, attempt login from a non-allowed IP and verify it is blocked.

### Step 4: Test JIT Provisioning

1. Remove any existing Velora account for a test user.
2. Have the user sign in via Azure AD SSO.
3. Verify the account is created with the correct role.

### Step 5: Test Group Changes

1. In Azure AD, move a test user between security groups.
2. Have the user log in again.
3. Verify their Velora role updates accordingly.

---

## 9. Troubleshooting

### 9.1 "AADSTS50011: The redirect URI does not match"

**Symptom:** Azure displays error AADSTS50011 after authentication attempt.

**Cause:** The redirect URI in the App Registration does not match what Velora sends.

**Fix:**
1. In Azure Portal, go to **App registrations** > **Velora TPRM** > **Authentication**.
2. Under **Platform configurations** > **Web**, verify the redirect URI is exactly `https://{your-domain}/auth/callback/azure`.
3. Check for trailing slashes, protocol mismatches, or port numbers.
4. Click **Save** and retry.

### 9.2 "AADSTS700016: Application not found in the directory"

**Symptom:** Azure displays error AADSTS700016.

**Cause:** The Client ID in Velora does not match any App Registration in the tenant, or the app was registered in a different tenant.

**Fix:**
1. Verify the Client ID in Velora matches the Application (client) ID on the App Registration Overview page.
2. Verify the Tenant ID matches the Directory (tenant) ID.
3. If using a multi-tenant setup, ensure the app is configured for "Accounts in any organizational directory."

### 9.3 "AADSTS7000215: Invalid client secret"

**Symptom:** Token exchange fails with AADSTS7000215.

**Cause:** The client secret is expired, incorrect, or was never properly saved.

**Fix:**
1. In Azure Portal, go to **App registrations** > **Velora TPRM** > **Certificates & secrets**.
2. Check the **Expires** column. If the secret has expired, create a new one.
3. Copy the new secret Value and update it in Velora.

### 9.4 Groups Claim Missing or Empty

**Symptom:** Users authenticate but receive the default role instead of their group-mapped role.

**Cause:** Group claims are not configured in the token, or the user is not a member of any mapped group.

**Fix:**
1. Verify the groups claim is configured in **Token configuration** (Section 5).
2. In Azure AD, verify the user is a direct member of the security group (nested groups may not be resolved depending on configuration).
3. If using App Roles, verify the `roles` claim appears and that Velora's **Groups Claim Name** is set to `roles`.
4. Check if the user has more than 200 groups (overage scenario). Verify that `GroupMember.Read.All` permission is granted and admin-consented.

### 9.5 "AADSTS65001: The user or administrator has not consented"

**Symptom:** Users see a consent error or are prompted for admin consent.

**Cause:** Admin consent has not been granted for the required API permissions.

**Fix:**
1. Go to **App registrations** > **Velora TPRM** > **API permissions**.
2. Click **Grant admin consent for {your-org}**.
3. Confirm the action.

### 9.6 "Need admin approval" Screen for Users

**Symptom:** Non-admin users see a "Need admin approval" page instead of being authenticated.

**Cause:** The app requires permissions that need admin consent, and it has not been granted.

**Fix:** Same as 9.5 -- grant admin consent in the Azure Portal.

### 9.7 Conditional Access Blocking Unexpectedly

**Symptom:** Users who should have access are being blocked.

**Fix:**
1. In Azure Portal, go to **Azure AD** > **Sign-in logs**.
2. Find the failed sign-in attempt.
3. Click on it and check the **Conditional Access** tab to see which policy blocked access and why.
4. Adjust the policy's conditions, exclusions, or user assignments.

### 9.8 Infinite Redirect Loop

**Symptom:** Browser redirects continuously between Velora and Microsoft login.

**Fix:**
1. Clear browser cookies for both domains.
2. Ensure Velora uses HTTPS.
3. Verify the redirect URI domain matches the Velora domain exactly.
4. Check that the ID token is being requested (not just an access token). In the App Registration's **Authentication** section, ensure **ID tokens** is checked under "Implicit grant and hybrid flows" (or that OIDC code flow is correctly configured).

---

## 10. Security Considerations

### Client Secret Rotation

- Azure AD client secrets have a maximum lifetime of 24 months.
- Set a calendar reminder to rotate secrets at least 2 weeks before expiry.
- Rotation process: Create a new secret in Azure > update in Velora > verify login works > delete the old secret in Azure.
- For higher security, consider using **Certificates** instead of client secrets. Upload a certificate in Azure under **Certificates & secrets** > **Certificates** tab.

### Token Configuration

- Velora requests only the minimum required scopes.
- ID tokens are validated server-side: signature verification against JWKS, issuer validation, audience validation, expiry check.
- Access tokens for Microsoft Graph calls (group overage) are stored server-side and never exposed to the browser.

### Least Privilege

- The `GroupMember.Read.All` permission is the minimum needed for group-based role mapping. Do not grant `Directory.Read.All` or `User.ReadWrite.All` unless specifically needed.
- Use **Assignment required = Yes** on the Enterprise Application to restrict who can authenticate.

### Session Security

- Configure sign-in frequency via Conditional Access (recommended: 8 hours for standard users, 1 hour for admins).
- Enable **Persistent browser session = Never** in Conditional Access for Velora to prevent "keep me signed in" behavior.

### Audit and Monitoring

- Azure AD sign-in logs capture every authentication attempt to Velora. Access at **Azure AD** > **Sign-in logs**, filter by Application = "Velora TPRM."
- Velora's internal audit log records all SSO events (logins, JIT provisioning, role changes).
- Set up Azure Monitor alerts for:
  - Unusual sign-in activity to the Velora application.
  - Failed sign-in spikes (may indicate credential stuffing).
  - Changes to the App Registration (client secret rotation, permission changes).

### Service Principal Security

- Do not grant the Velora service principal any roles in Azure AD beyond what is required.
- Periodically review the App Registration's **API permissions** and remove any that are no longer needed.

### Network Security

- Use Conditional Access named locations to restrict Velora access to corporate networks/VPNs.
- Velora supports IP allowlisting under **Admin** > **Security** > **Network Policies** as an additional layer.

### Break-Glass Accounts

- Always exclude at least two break-glass admin accounts from Conditional Access policies.
- These accounts should use local Velora authentication (not SSO) as a fallback.
- Store break-glass credentials securely (e.g., in a hardware security module or sealed envelope).

---

*Document maintained by the Velora TPRM platform team. For support, contact your Velora administrator or open a ticket in your internal IT service management system.*
