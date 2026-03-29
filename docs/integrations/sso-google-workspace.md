# Velora TPRM -- Google Workspace SSO Integration Guide

**Version:** 1.0.0
**Last Updated:** 2026-03-29
**Applies To:** Velora TPRM v2.1.0+
**Protocol:** OIDC (OpenID Connect via Google OAuth 2.0)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Google Cloud Console OAuth Setup](#2-google-cloud-console-oauth-setup)
3. [Domain Verification](#3-domain-verification)
4. [Configure SSO in Velora TPRM](#4-configure-sso-in-velora-tprm)
5. [Google Groups for Role Mapping](#5-google-groups-for-role-mapping)
6. [Just-In-Time (JIT) User Provisioning](#6-just-in-time-jit-user-provisioning)
7. [Testing the SSO Connection](#7-testing-the-sso-connection)
8. [Troubleshooting](#8-troubleshooting)
9. [Security Considerations](#9-security-considerations)

---

## 1. Prerequisites

| Requirement | Detail |
|---|---|
| Google Workspace account | A Google Workspace (Business, Enterprise, or Education) subscription. Personal Gmail accounts are not supported for organizational SSO. |
| Google Admin role | Super Admin access to the Google Admin Console (`admin.google.com`) |
| Google Cloud access | Owner or Editor role on a Google Cloud project |
| Velora TPRM instance | Running v2.1.0 or later, accessible via HTTPS |
| Custom domain | A verified domain for Velora (e.g., `tprm.yourcompany.com`) |
| TLS certificate | Valid TLS certificate on your Velora domain |
| Velora admin access | An account with `Platform Administrator` role in Velora TPRM |
| Google Groups | Pre-created groups for Velora role mapping (see Section 5) |

---

## 2. Google Cloud Console OAuth Setup

### Step 1: Open Google Cloud Console

1. Navigate to `https://console.cloud.google.com`.
2. Sign in with a Google Workspace admin account.

### Step 2: Select or Create a Project

1. In the top navigation bar, click the **project selector** dropdown (to the right of "Google Cloud").
2. Either select an existing project or click **New Project**:
   - **Project name:** `Velora TPRM SSO`
   - **Organization:** Select your organization.
   - **Location:** Select your organization or a folder.
3. Click **Create** and wait for the project to be created.
4. Ensure the new project is selected in the project selector.

### Step 3: Configure the OAuth Consent Screen

This step is required before creating OAuth credentials.

1. In the left sidebar, navigate to **APIs & Services** > **OAuth consent screen**.
   - Alternatively, search "OAuth consent screen" in the top search bar.
2. Select **User Type:**
   - **Internal** -- Only users within your Google Workspace organization can authenticate. This is the recommended setting for enterprise SSO.
   - **External** -- Any Google account can authenticate (requires Google verification for production). Only use this for multi-tenant deployments.
3. Click **Create**.

Fill in the consent screen details:

| Field | Value |
|---|---|
| **App name** | `Velora TPRM` |
| **User support email** | Your IT support email (e.g., `it-support@yourcompany.com`) |
| **App logo** | (Optional) Upload your company or Velora logo |
| **Application home page** | `https://{your-domain}` |
| **Application privacy policy link** | `https://{your-domain}/privacy` |
| **Application terms of service link** | `https://{your-domain}/terms` |
| **Authorized domains** | Add your Velora domain (e.g., `yourcompany.com`) |
| **Developer contact information** | Your IT admin email |

4. Click **Save and Continue**.

### Step 4: Configure Scopes

1. On the "Scopes" page, click **Add or Remove Scopes**.
2. Add the following scopes:

| Scope | Purpose |
|---|---|
| `openid` | Required for OIDC authentication |
| `https://www.googleapis.com/auth/userinfo.email` | Access user's email address |
| `https://www.googleapis.com/auth/userinfo.profile` | Access user's name and profile picture |
| `https://www.googleapis.com/auth/admin.directory.group.readonly` | Read Google Groups membership (required for role mapping) |

3. Click **Update**, then **Save and Continue**.
4. On the "Test users" page (for External type only), add test users if needed. For Internal type, skip this.
5. Click **Save and Continue**, then **Back to Dashboard**.

### Step 5: Create OAuth 2.0 Credentials

1. In the left sidebar, go to **APIs & Services** > **Credentials**.
2. Click **+ Create Credentials** at the top of the page.
3. Select **OAuth client ID**.
4. Configure:

| Field | Value |
|---|---|
| **Application type** | **Web application** |
| **Name** | `Velora TPRM OAuth Client` |
| **Authorized JavaScript origins** | `https://{your-domain}` |
| **Authorized redirect URIs** | `https://{your-domain}/auth/callback/google` |

5. Click **Create**.

### Step 6: Collect Credentials

A dialog appears with your credentials. Record these values:

| Field | Value |
|---|---|
| **Client ID** | A long string ending in `.apps.googleusercontent.com` |
| **Client Secret** | A string starting with `GOCSPX-` |

Click **Download JSON** to save a backup of these credentials. Store this file securely -- it contains your client secret.

> **Security Note:** Never commit this JSON file to version control. Never share it in email or chat.

### Step 7: Enable Required APIs

1. In the left sidebar, go to **APIs & Services** > **Library**.
2. Search for and enable each of the following APIs:

| API | Purpose |
|---|---|
| **Google Identity Toolkit API** | Core identity authentication |
| **Admin SDK API** | Required for Google Groups membership lookup |
| **Google People API** | User profile information |

For each API:
1. Click on the API name in search results.
2. Click **Enable**.

---

## 3. Domain Verification

Domain verification proves to Google that you own the domain Velora runs on. This is required for Internal OAuth consent screens and to ensure redirect URIs are authorized.

### Option A: Already Verified in Google Workspace

If your Velora domain is the same as (or a subdomain of) your Google Workspace primary domain, it is likely already verified.

1. Go to **Google Admin Console** > **Account** > **Domains** > **Manage domains**.
2. Verify your domain appears with a "Verified" status.

### Option B: Verify a New Domain

If Velora runs on a different domain:

1. Go to Google Cloud Console > **APIs & Services** > **OAuth consent screen** > **Edit App**.
2. Under **Authorized domains**, add your Velora domain.
3. Google may require domain verification via Google Search Console:
   a. Go to `https://search.google.com/search-console`.
   b. Click **Add property** > **URL prefix** > enter `https://{your-domain}`.
   c. Choose a verification method:
      - **DNS record** (recommended): Add a TXT record to your domain's DNS.
      - **HTML file upload**: Upload a verification file to `https://{your-domain}/google{code}.html`.
      - **HTML tag**: Add a meta tag to your Velora landing page.
   d. Complete verification and return to the OAuth consent screen setup.

### Option C: Subdomain of Verified Domain

If your Velora domain is a subdomain of an already-verified domain (e.g., `tprm.yourcompany.com` where `yourcompany.com` is verified), Google automatically trusts it. No additional verification is needed.

---

## 4. Configure SSO in Velora TPRM

### Step 1: Navigate to SSO Settings

1. Log into Velora TPRM with a Platform Administrator account.
2. Click the **gear icon** in the bottom-left of the sidebar to open **Admin Settings**.
3. Navigate to **Integrations** > **SSO**.

### Step 2: Select Identity Provider

1. Click **Add SSO Provider**.
2. Select **Google Workspace** from the provider list.

### Step 3: Enter Configuration

| Velora Field | Value |
|---|---|
| **Protocol** | OIDC |
| **Client ID** | The Client ID from Section 2, Step 6 (ending in `.apps.googleusercontent.com`) |
| **Client Secret** | The Client Secret from Section 2, Step 6 |
| **Issuer URL** | `https://accounts.google.com` |
| **Redirect URI** | `https://{your-domain}/auth/callback/google` (auto-populated) |
| **Scopes** | `openid email profile` |
| **Hosted Domain (hd)** | `yourcompany.com` (restricts login to your Google Workspace domain) |
| **Groups Claim Source** | `Google Directory API` (see Section 5) |

### Step 4: Configure Service Account for Groups (Required for Role Mapping)

Google does not include group membership in OIDC tokens natively. Velora uses a service account with domain-wide delegation to query Google Directory API for group membership.

1. In Google Cloud Console, go to **IAM & Admin** > **Service Accounts**.
2. Click **+ Create Service Account**.
3. Fill in:
   - **Name:** `Velora TPRM Groups Reader`
   - **Description:** `Reads Google Groups membership for Velora role mapping`
4. Click **Create and Continue**.
5. Skip the "Grant this service account access" step (click **Continue**).
6. Skip the "Grant users access" step (click **Done**).

7. On the Service Accounts list, click the newly created service account.
8. Go to the **Keys** tab.
9. Click **Add Key** > **Create new key**.
10. Select **JSON** and click **Create**.
11. A JSON key file downloads. Store this securely.

12. Go to the **Details** tab. Copy the **Unique ID** (a numeric string) and the **Email** (e.g., `velora-tprm-groups@your-project.iam.gserviceaccount.com`).

### Step 5: Enable Domain-Wide Delegation

1. On the service account detail page, click **Show Advanced Settings** (or the edit icon).
2. Check **Enable Google Workspace Domain-wide Delegation**.
3. Click **Save**.

4. Now go to **Google Admin Console** (`admin.google.com`).
5. Navigate to **Security** > **API Controls** > **Manage Domain-wide Delegation**.
   - Path: Admin console sidebar > **Security** > **Access and data control** > **API controls** > scroll to **Domain-wide delegation** > **Manage Domain Wide Delegation**.
6. Click **Add new**.
7. Fill in:
   - **Client ID:** The numeric Unique ID of the service account.
   - **OAuth scopes:** `https://www.googleapis.com/auth/admin.directory.group.readonly`
8. Click **Authorize**.

### Step 6: Upload Service Account Key to Velora

1. Back in Velora Admin > **Integrations** > **SSO** > **Google Workspace** configuration.
2. In the **Service Account Configuration** section:
   - Upload the JSON key file from Step 4.
   - **Admin Email for Delegation:** Enter a Google Workspace Super Admin email. The service account impersonates this user to query the Directory API. This admin does not need to log into Velora.
3. Click **Save Configuration**.

---

## 5. Google Groups for Role Mapping

### Step 1: Create Google Groups

In Google Admin Console (`admin.google.com`):

1. Go to **Directory** > **Groups**.
2. Click **Create group** for each Velora role:

| Group Name | Group Email | Description |
|---|---|---|
| Velora Platform Admins | `velora-platform-admins@yourcompany.com` | Velora system administrators |
| Velora Risk Managers | `velora-risk-managers@yourcompany.com` | Risk assessment managers |
| Velora Analysts | `velora-analysts@yourcompany.com` | Risk assessment analysts |
| Velora Vendor Managers | `velora-vendor-managers@yourcompany.com` | Vendor relationship managers |
| Velora Auditors | `velora-auditors@yourcompany.com` | Read-only audit access |
| Velora Viewers | `velora-viewers@yourcompany.com` | Dashboard view only |

3. For each group, add the appropriate members via **Members** > **Add members**.

### Step 2: Configure Role Mapping in Velora

1. In Velora Admin, go to **Integrations** > **SSO** > **Role Mapping** tab.
2. Map each Google Group email to a Velora role:

| Google Group Email | Velora Role |
|---|---|
| `velora-platform-admins@yourcompany.com` | Platform Administrator |
| `velora-risk-managers@yourcompany.com` | Risk Manager |
| `velora-analysts@yourcompany.com` | Risk Analyst |
| `velora-vendor-managers@yourcompany.com` | Vendor Manager |
| `velora-auditors@yourcompany.com` | Auditor |
| `velora-viewers@yourcompany.com` | Viewer |

3. Set a **Default Role** for users not in any mapped group (recommended: `Viewer`).
4. Configure **Multi-Group Behavior** (Highest privilege wins / First match / Deny).
5. Click **Save**.

### How Group Resolution Works

1. User authenticates via Google OAuth.
2. Velora receives the user's email from the ID token.
3. Velora's backend uses the service account to call Google Directory API: `GET https://admin.googleapis.com/admin/directory/v1/groups?userKey={user-email}`.
4. The API returns all groups the user belongs to.
5. Velora matches group emails against the role mapping table.
6. The highest-privilege matching role is assigned.

---

## 6. Just-In-Time (JIT) User Provisioning

### Step 1: Enable JIT Provisioning

1. In Velora Admin, go to **Integrations** > **SSO** > **Provisioning** tab.
2. Toggle **Enable JIT Provisioning** to ON.

### Step 2: Configure JIT Settings

| Setting | Recommended Value | Description |
|---|---|---|
| **Auto-create users** | Enabled | Create accounts on first SSO login |
| **Default role for JIT users** | Viewer | Role assigned if no group mapping matches |
| **Update profile on login** | Enabled | Sync name/email/profile picture from Google |
| **Update group membership on login** | Enabled | Re-query Google Groups and update role on each login |
| **Deactivate on group removal** | Enabled | Deactivate if removed from all mapped groups |
| **Allowed email domains** | `yourcompany.com` | Must match the hosted domain (hd) parameter |

### Step 3: Save

Click **Save Provisioning Settings**.

---

## 7. Testing the SSO Connection

### Step 1: Use the Built-in Test

1. In Velora Admin, go to **Integrations** > **SSO**.
2. Click **Test Connection**.
3. A new tab opens and redirects to Google's login page.
4. Select your Google Workspace account.
5. If prompted, grant consent for the requested scopes.
6. After redirect, Velora displays test results:
   - Authentication status.
   - Claims received (email, name, hosted domain).
   - Google Groups resolved via Directory API.
   - Mapped Velora role.
   - Warnings or errors.

### Step 2: Test Service Account Connectivity

1. In Velora Admin, go to **Integrations** > **SSO** > **Google Workspace** configuration.
2. Click **Test Directory API Connection**.
3. This verifies:
   - The service account key is valid.
   - Domain-wide delegation is properly configured.
   - The Admin SDK API is enabled.
   - Group membership can be queried.

### Step 3: Test with a Non-Admin User

1. Open an incognito/private browser window.
2. Navigate to `https://{your-domain}/login`.
3. Click **Sign in with Google**.
4. Sign in with a non-admin Google Workspace account that belongs to one of the mapped groups.
5. Verify:
   - Correct dashboard loads.
   - Role and permissions match the expected group mapping.
   - User appears in Velora Admin > **Users** with "SSO (Google)" as auth method.

### Step 4: Test JIT Provisioning

1. Remove any existing Velora account for a test user.
2. Have the user sign in via Google SSO.
3. Verify the account is created with the correct role.

### Step 5: Test Group Changes

1. In Google Admin Console, move a test user between Google Groups.
2. Allow up to 10 minutes for group membership changes to propagate in Google's directory (propagation delay is normal).
3. Have the user log in again.
4. Verify their Velora role updates accordingly.

---

## 8. Troubleshooting

### 8.1 "Error 400: redirect_uri_mismatch"

**Symptom:** Google displays "Error 400: redirect_uri_mismatch" after clicking Sign in.

**Cause:** The redirect URI sent by Velora does not match what is configured in Google Cloud Console.

**Fix:**
1. In Google Cloud Console, go to **APIs & Services** > **Credentials**.
2. Click on your OAuth client (Velora TPRM OAuth Client).
3. Under **Authorized redirect URIs**, verify the URI is exactly `https://{your-domain}/auth/callback/google`.
4. Common mistakes:
   - Missing `https://` (http is not allowed for production).
   - Trailing slash mismatch (`/callback/google` vs `/callback/google/`).
   - Wrong domain or port number.
5. Save and retry.

### 8.2 "Error 403: access_denied" or "This app is blocked"

**Symptom:** Google displays "This app is blocked" or error 403.

**Cause:** The OAuth consent screen is in "Testing" mode (External type), or the app has not been verified by Google.

**Fix:**
- If using **Internal** user type: This error should not occur. Verify the user is in your Google Workspace organization.
- If using **External** user type: Either add the user as a test user in the OAuth consent screen, or submit the app for Google verification.

### 8.3 "Error 401: invalid_client"

**Symptom:** Token exchange fails with `invalid_client`.

**Cause:** Client ID or Client Secret is incorrect.

**Fix:**
1. In Google Cloud Console, go to **Credentials**.
2. Verify the Client ID matches what is in Velora.
3. If the Client Secret may be wrong, click the download button to re-download the JSON. Create a new secret if needed.
4. Update Velora with the correct values.

### 8.4 Groups Not Being Resolved

**Symptom:** User authenticates but receives the default role. Groups are empty in test results.

**Possible causes and fixes:**

**a) Service account key is invalid or expired:**
1. In Google Cloud Console, go to **Service Accounts** > click account > **Keys** tab.
2. If the key is expired or deleted, create a new one and upload to Velora.

**b) Domain-wide delegation not configured:**
1. In Google Admin Console, go to **Security** > **API Controls** > **Domain-wide Delegation**.
2. Verify the service account's Client ID is listed with the correct scope.

**c) Admin SDK API not enabled:**
1. In Google Cloud Console, go to **APIs & Services** > **Enabled APIs**.
2. Search for "Admin SDK API." If not enabled, go to the Library and enable it.

**d) Admin email for delegation is incorrect:**
1. The impersonation email must be a Super Admin in Google Workspace.
2. Verify in Velora's SSO configuration that the Admin Email for Delegation is correct.

**e) Google Groups propagation delay:**
1. After adding a user to a group, allow up to 10 minutes for changes to propagate.
2. Retry the login after waiting.

### 8.5 "Error: 'hd' claim does not match expected domain"

**Symptom:** Velora rejects the authentication with a hosted domain mismatch.

**Cause:** The user's Google account is not in the expected Workspace domain.

**Fix:**
1. Verify the user is logging in with their organizational Google account, not a personal Gmail account.
2. In Velora's SSO configuration, verify the **Hosted Domain (hd)** field matches your Google Workspace domain.

### 8.6 OAuth Consent Screen Prompts Repeatedly

**Symptom:** Users are asked to grant consent every time they log in.

**Cause:** The consent screen is in Testing mode (External type), which revokes consent after 7 days.

**Fix:**
- Switch to **Internal** user type if all users are in your organization.
- If External is required, submit the app for Google verification to move to production.

### 8.7 "Error 403: forbidden" from Directory API

**Symptom:** Velora logs show a 403 error when querying Google Directory API.

**Cause:** The service account does not have permission to query groups.

**Fix:**
1. Verify domain-wide delegation is set up with the scope `https://www.googleapis.com/auth/admin.directory.group.readonly`.
2. Verify the delegation uses the correct Client ID (the numeric ID, not the email).
3. Verify the Admin SDK API is enabled in the Google Cloud project.

---

## 9. Security Considerations

### OAuth Client Secret Protection

- The Client Secret is encrypted at rest in Velora using AES-256-GCM.
- Never share the Client Secret via email, chat, or documentation.
- Rotate the Client Secret periodically (recommended: every 6 months).
  - Rotation process: Create a new credential in Google Cloud Console > update in Velora > verify login > delete the old credential.

### Service Account Key Security

- The service account JSON key provides privileged access to your Google Directory.
- Store it in Velora's encrypted configuration store only. Do not keep copies in shared drives, email, or chat.
- Rotate service account keys every 12 months.
  - Rotation: Create new key > upload to Velora > verify Directory API works > delete old key in Google Cloud Console.
- Consider using **Workload Identity Federation** instead of key files for higher security environments.

### Hosted Domain Enforcement

- Always configure the `hd` (hosted domain) parameter in Velora to restrict authentication to your Google Workspace domain.
- Without this, any Google account could attempt to authenticate (though they would fail at group resolution).
- Velora validates the `hd` claim server-side. The client-side `hd` hint to Google is a UX convenience, not a security control.

### Domain-Wide Delegation Scope Restriction

- Grant only the minimum required scope: `admin.directory.group.readonly`.
- Do not grant broader scopes like `admin.directory.user.readonly` or `admin.directory.group` (read-write) unless specifically needed.
- Periodically audit domain-wide delegation entries in Google Admin Console and remove unused ones.

### Session Management

- Google OAuth tokens issued to Velora have a 1-hour lifetime by default.
- Velora uses refresh tokens to maintain sessions beyond the token lifetime.
- Configure maximum session duration in Velora under **Admin** > **Security** > **Session Policy**:
  - Recommended: 8 hours for standard users, 1 hour for administrators.
  - Idle timeout: 30 minutes.

### MFA Enforcement

- MFA is enforced at the Google Workspace level, not in Velora.
- Configure MFA in Google Admin Console: **Security** > **2-Step Verification**.
- Recommended: Enforce 2-Step Verification for all organizational units that include Velora users.
- Use security keys (FIDO2) for administrator accounts.

### API Abuse Protection

- Google enforces rate limits on Directory API calls. Velora caches group membership for 5 minutes to reduce API calls.
- If you have a large organization, monitor API quotas in Google Cloud Console under **APIs & Services** > **Quotas**.

### Audit Logging

- All SSO authentication events are logged in Velora's audit log.
- Google Workspace Admin logs capture all OAuth consent grants and Directory API access in the Google Admin Console under **Reporting** > **Audit and investigation** > **OAuth log events**.
- Cross-reference both logs for complete visibility into authentication activity.

### Revoking Access

To immediately revoke a user's Velora access:

1. **Remove from Google Groups** -- Prevents role assignment on next login.
2. **Remove from Velora** -- Deactivate the user in Velora Admin > **Users**.
3. **Revoke Google OAuth tokens** -- In Google Admin Console, go to **Directory** > **Users** > select user > **Security** > **Connected applications** > Revoke Velora TPRM.
4. **Remove from OAuth client assignment** -- If using Google Workspace app assignment policies.

All four steps should be performed for complete revocation.

### Network Security

- Google OAuth endpoints use TLS 1.2+ exclusively.
- Velora validates Google's JWKS endpoint TLS certificate to prevent man-in-the-middle attacks.
- Configure Velora's network policies to restrict access by IP if needed (**Admin** > **Security** > **Network Policies**).

---

*Document maintained by the Velora TPRM platform team. For support, contact your Velora administrator or open a ticket in your internal IT service management system.*
