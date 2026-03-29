# Velora TPRM -- Okta SSO Integration Guide

**Version:** 1.0.0
**Last Updated:** 2026-03-29
**Applies To:** Velora TPRM v2.1.0+
**Protocol Support:** OIDC (recommended), SAML 2.0

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Option A -- OIDC Application Setup in Okta](#2-option-a--oidc-application-setup-in-okta)
3. [Option B -- SAML 2.0 Application Setup in Okta](#3-option-b--saml-20-application-setup-in-okta)
4. [Configure SSO in Velora TPRM](#4-configure-sso-in-velora-tprm)
5. [Group-to-Role Mapping](#5-group-to-role-mapping)
6. [Just-In-Time (JIT) User Provisioning](#6-just-in-time-jit-user-provisioning)
7. [Testing the SSO Connection](#7-testing-the-sso-connection)
8. [Troubleshooting](#8-troubleshooting)
9. [Security Considerations](#9-security-considerations)

---

## 1. Prerequisites

Before starting, confirm the following:

| Requirement | Detail |
|---|---|
| Okta account | Okta admin console access with `Application Admin` or `Super Admin` role |
| Velora TPRM instance | Running v2.1.0 or later, accessible via HTTPS |
| Domain | A verified custom domain for your Velora instance (e.g., `tprm.yourcompany.com`) |
| TLS certificate | Valid TLS certificate on your Velora domain (self-signed certificates are not supported) |
| DNS | DNS records pointing your custom domain to the Velora instance |
| Velora admin access | An account with `Platform Administrator` role in Velora TPRM |
| Okta groups | Pre-created Okta groups that map to Velora roles (see Section 5) |

---

## 2. Option A -- OIDC Application Setup in Okta

OIDC is the recommended protocol. It is simpler to configure, uses modern token-based authentication, and supports refresh tokens natively.

### Step 1: Open the Okta Admin Console

1. Navigate to `https://your-org.okta.com/admin/dashboard`.
2. Sign in with an account that has Application Admin privileges.

### Step 2: Create a New Application Integration

1. In the left sidebar, click **Applications** > **Applications**.
2. Click the **Create App Integration** button (top-left area of the applications list).
3. In the dialog that appears:
   - **Sign-in method:** Select **OIDC - OpenID Connect**.
   - **Application type:** Select **Web Application**.
4. Click **Next**.

### Step 3: Configure General Settings

On the "New Web App Integration" page, fill in:

| Field | Value |
|---|---|
| **App integration name** | `Velora TPRM` |
| **Logo** | (Optional) Upload your company or Velora logo |
| **Grant type** | Check **Authorization Code** (required). Optionally check **Refresh Token** for persistent sessions. |
| **Sign-in redirect URIs** | `https://{your-domain}/auth/callback/okta` |
| **Sign-out redirect URIs** | `https://{your-domain}/auth/logout/callback` |
| **Base URIs** | `https://{your-domain}` |

Replace `{your-domain}` with your actual Velora TPRM domain (e.g., `tprm.yourcompany.com`).

### Step 4: Configure Assignments

Under the **Assignments** section at the bottom of the page:

- Select **Limit access to selected groups** if you want to control which Okta users can access Velora.
- Add the Okta groups that should have Velora access.
- Alternatively, select **Allow everyone in your organization to access** for org-wide rollout.

Click **Save**.

### Step 5: Collect OIDC Credentials

After saving, Okta redirects you to the application detail page. Navigate to the **General** tab:

1. **Client ID** -- Displayed under "Client Credentials." Copy this value.
2. **Client Secret** -- Click **Show** next to the client secret field. Copy this value.
3. **Okta Domain** -- This is your Okta org URL, visible in the browser address bar (e.g., `your-org.okta.com`). You will need this to construct the issuer URL.

Construct the following URLs:

| URL Type | Value |
|---|---|
| **Issuer URI** | `https://your-org.okta.com/oauth2/default` |
| **Authorization Endpoint** | `https://your-org.okta.com/oauth2/default/v1/authorize` |
| **Token Endpoint** | `https://your-org.okta.com/oauth2/default/v1/token` |
| **UserInfo Endpoint** | `https://your-org.okta.com/oauth2/default/v1/userinfo` |
| **JWKS URI** | `https://your-org.okta.com/oauth2/default/v1/keys` |

If you use a custom Authorization Server instead of `default`, replace `default` with your server ID.

### Step 6: Configure Scopes

1. On the application detail page, go to the **Okta API Scopes** tab.
2. Ensure the following scopes are granted:
   - `openid`
   - `profile`
   - `email`
   - `groups` (required for role mapping)

### Step 7: Add Groups Claim to ID Token

This step is required for group-to-role mapping.

1. In the left sidebar, go to **Security** > **API**.
2. Click on the **default** authorization server (or whichever server you are using).
3. Go to the **Claims** tab.
4. Click **Add Claim**.
5. Fill in:

| Field | Value |
|---|---|
| **Name** | `groups` |
| **Include in token type** | **ID Token** (select "Always") |
| **Value type** | **Groups** |
| **Filter** | **Matches regex** with value `.*` (to include all groups), or specify a prefix like `velora-` to limit to Velora-related groups |
| **Include in** | Select the scopes: `openid`, `profile`, `groups` |

6. Click **Create**.

---

## 3. Option B -- SAML 2.0 Application Setup in Okta

Use SAML 2.0 if your organization requires it for compliance or if you already have a SAML-based SSO infrastructure.

### Step 1: Create a SAML Application

1. In the Okta Admin Console, go to **Applications** > **Applications**.
2. Click **Create App Integration**.
3. Select **SAML 2.0**, then click **Next**.

### Step 2: General Settings

| Field | Value |
|---|---|
| **App name** | `Velora TPRM` |
| **App logo** | (Optional) |

Click **Next**.

### Step 3: SAML Settings

| Field | Value |
|---|---|
| **Single sign-on URL** | `https://{your-domain}/auth/saml/callback` |
| **Audience URI (SP Entity ID)** | `https://{your-domain}/auth/saml/metadata` |
| **Default RelayState** | (Leave blank) |
| **Name ID format** | `EmailAddress` |
| **Application username** | `Okta username` |

Under **Attribute Statements**, add:

| Name | Name format | Value |
|---|---|---|
| `email` | URI Reference | `user.email` |
| `firstName` | URI Reference | `user.firstName` |
| `lastName` | URI Reference | `user.lastName` |

Under **Group Attribute Statements**, add:

| Name | Name format | Filter |
|---|---|---|
| `groups` | URI Reference | Matches regex: `.*` (or a prefix filter like `velora-`) |

Click **Next**, then **Finish**.

### Step 4: Collect SAML Metadata

1. On the application page, go to the **Sign On** tab.
2. Under **SAML Signing Certificates**, find the active certificate.
3. Click **Actions** > **View IdP metadata**. This opens an XML page.
4. Copy the metadata URL (the URL in the browser bar). You will paste this into Velora.
5. Alternatively, click **Download certificate** for manual configuration.

Key values from the metadata:

| Field | Where to Find |
|---|---|
| **IdP SSO URL** | `SingleSignOnService` element `Location` attribute |
| **IdP Issuer** | `entityID` attribute in the root element |
| **X.509 Certificate** | Inside the `X509Certificate` element |

---

## 4. Configure SSO in Velora TPRM

### Step 1: Navigate to SSO Settings

1. Log into Velora TPRM with a Platform Administrator account.
2. Click the **gear icon** in the bottom-left of the sidebar to open **Admin Settings**.
3. In the Admin panel, navigate to **Integrations** > **SSO**.

### Step 2: Select Identity Provider

1. Click **Add SSO Provider**.
2. Select **Okta** from the provider list.

### Step 3: Enter Configuration (OIDC)

If you set up OIDC in Section 2, fill in:

| Velora Field | Value |
|---|---|
| **Protocol** | OIDC |
| **Client ID** | The Client ID from Okta (Step 5 of Section 2) |
| **Client Secret** | The Client Secret from Okta (Step 5 of Section 2) |
| **Issuer URL** | `https://your-org.okta.com/oauth2/default` |
| **Redirect URI** | `https://{your-domain}/auth/callback/okta` (auto-populated) |
| **Scopes** | `openid profile email groups` |
| **Groups Claim Name** | `groups` |

### Step 3 (Alt): Enter Configuration (SAML 2.0)

If you set up SAML in Section 3, fill in:

| Velora Field | Value |
|---|---|
| **Protocol** | SAML 2.0 |
| **IdP Metadata URL** | The metadata URL from Okta (Step 4 of Section 3) |
| **IdP SSO URL** | From the metadata XML |
| **IdP Issuer / Entity ID** | From the metadata XML |
| **X.509 Certificate** | Paste the certificate content |
| **SP Entity ID** | `https://{your-domain}/auth/saml/metadata` (auto-populated) |
| **Name ID Format** | `EmailAddress` |

### Step 4: Save and Verify

1. Click **Save Configuration**.
2. Velora performs a metadata validation check. If it passes, the status indicator turns green.
3. If validation fails, review the error message and correct the configuration.

---

## 5. Group-to-Role Mapping

Velora TPRM maps Okta groups to internal roles. This determines what permissions an SSO user receives upon login.

### Step 1: Navigate to Role Mapping

1. In Velora Admin, go to **Integrations** > **SSO** > **Role Mapping** tab.

### Step 2: Define Mappings

Map each Okta group name to a Velora role:

| Okta Group Name | Velora Role | Description |
|---|---|---|
| `velora-platform-admins` | Platform Administrator | Full system administration |
| `velora-risk-managers` | Risk Manager | Manage vendor risk assessments, set thresholds |
| `velora-analysts` | Risk Analyst | Conduct assessments, review evidence |
| `velora-vendor-managers` | Vendor Manager | Manage vendor relationships, onboarding |
| `velora-auditors` | Auditor | Read-only access to all risk data and reports |
| `velora-viewers` | Viewer | Read-only access to dashboards |

### Step 3: Configure Default Role

Set a **Default Role** for users who authenticate via SSO but do not belong to any mapped group. Recommended: `Viewer` (minimum privilege).

### Step 4: Configure Multi-Group Behavior

If a user belongs to multiple Okta groups:

- **Highest privilege wins** (default) -- User receives the role with the broadest permissions.
- **First match wins** -- User receives the role of the first matching group in the list order.
- **Deny access** -- Users in multiple mapped groups are denied access until resolved by an admin.

Select your preferred behavior and click **Save**.

---

## 6. Just-In-Time (JIT) User Provisioning

JIT provisioning automatically creates Velora user accounts the first time an Okta-authenticated user logs in, eliminating the need to pre-create accounts.

### Step 1: Enable JIT Provisioning

1. In Velora Admin, go to **Integrations** > **SSO** > **Provisioning** tab.
2. Toggle **Enable JIT Provisioning** to ON.

### Step 2: Configure JIT Settings

| Setting | Recommended Value | Description |
|---|---|---|
| **Auto-create users** | Enabled | Create accounts on first SSO login |
| **Default role for JIT users** | Viewer | Role assigned if no group mapping matches |
| **Update profile on login** | Enabled | Sync name/email changes from Okta on each login |
| **Update group membership on login** | Enabled | Re-evaluate role based on current Okta groups |
| **Deactivate on group removal** | Enabled | Deactivate Velora account if user is removed from all mapped Okta groups |
| **Allowed email domains** | `yourcompany.com` | Restrict JIT provisioning to specific email domains |

### Step 3: Save

Click **Save Provisioning Settings**.

### How JIT Works at Runtime

1. User clicks "Sign in with Okta" on the Velora login page.
2. User authenticates in Okta and is redirected back with an ID token.
3. Velora checks if an account exists for the email in the token.
4. If no account exists and JIT is enabled, Velora creates one using the token claims (`email`, `firstName`, `lastName`, `groups`).
5. The user is assigned a role based on the group-to-role mapping.
6. The user is logged in.

---

## 7. Testing the SSO Connection

### Step 1: Use the Built-in Test

1. In Velora Admin, go to **Integrations** > **SSO**.
2. Click **Test Connection**.
3. A new browser tab opens, redirecting you to Okta for authentication.
4. After authenticating, you are redirected back to Velora.
5. The test results page displays:
   - Whether authentication succeeded.
   - The claims received (email, name, groups).
   - The Velora role that would be assigned.
   - Any warnings (e.g., unrecognized groups).

### Step 2: Test with a Non-Admin User

1. Open an incognito/private browser window.
2. Navigate to `https://{your-domain}/login`.
3. Click **Sign in with Okta**.
4. Sign in with a non-admin Okta account that belongs to one of the mapped groups.
5. Verify:
   - The user lands on the correct Velora dashboard.
   - The user has the expected role and permissions.
   - The user appears in Velora Admin > **Users** with the correct role and "SSO (Okta)" as the auth method.

### Step 3: Test JIT Provisioning

1. Remove any existing Velora account for a test user.
2. Have that user sign in via Okta SSO.
3. Verify the account is auto-created with the correct role.

### Step 4: Test Group Changes

1. In Okta, move a test user from one Velora group to another.
2. Have the user log in again.
3. Verify their Velora role updates to match the new group (if "Update group membership on login" is enabled).

---

## 8. Troubleshooting

### 8.1 "Redirect URI Mismatch" Error

**Symptom:** Okta displays "The redirect URI is not allowed" or a 400 error after authentication.

**Cause:** The redirect URI in Velora does not match what is configured in the Okta application.

**Fix:**
1. In Okta Admin Console, go to **Applications** > **Velora TPRM** > **General** tab.
2. Under "Login," verify that the **Sign-in redirect URI** is exactly `https://{your-domain}/auth/callback/okta`.
3. Ensure there are no trailing slashes, no protocol mismatches (http vs https), and no typos.
4. Save and retry.

### 8.2 "Invalid Client" Error

**Symptom:** Token exchange fails with `invalid_client`.

**Cause:** Client ID or Client Secret is incorrect.

**Fix:**
1. In Okta, go to the application's **General** tab.
2. Verify the Client ID matches what is entered in Velora.
3. Regenerate the Client Secret in Okta, then update it in Velora.

### 8.3 Groups Not Appearing in Token

**Symptom:** User authenticates but receives the default role instead of their group-mapped role.

**Cause:** The `groups` claim is not included in the ID token.

**Fix:**
1. In Okta Admin, go to **Security** > **API** > **default** authorization server > **Claims**.
2. Verify a `groups` claim exists with "Include in token type" set to **ID Token**.
3. Verify the filter includes the groups your users belong to.
4. In the Okta application, ensure the `groups` scope is requested.
5. In Velora, verify the **Groups Claim Name** field is set to `groups`.

### 8.4 "User Not Assigned to This Application" Error

**Symptom:** User gets "You are not assigned to this application" in Okta.

**Cause:** The user (or their group) is not assigned to the Okta application.

**Fix:**
1. In Okta Admin, go to **Applications** > **Velora TPRM** > **Assignments** tab.
2. Add the user directly, or add the Okta group the user belongs to.

### 8.5 SAML Certificate Expiration

**Symptom:** SAML authentication suddenly stops working after previously working fine.

**Cause:** The Okta SAML signing certificate has expired.

**Fix:**
1. In Okta Admin, go to **Applications** > **Velora TPRM** > **Sign On** tab.
2. Under SAML Signing Certificates, check the expiration date.
3. If expired, generate a new certificate and update the X.509 certificate in Velora.

### 8.6 Clock Skew

**Symptom:** Token validation fails intermittently with "token not yet valid" or "token expired."

**Cause:** The server clocks between Okta and Velora are out of sync.

**Fix:**
1. Ensure NTP is configured and running on the Velora server.
2. Velora allows up to 60 seconds of clock skew by default. If you need more, set `SSO_CLOCK_SKEW_TOLERANCE` in your environment configuration.

### 8.7 Infinite Redirect Loop

**Symptom:** Browser keeps redirecting between Velora and Okta without completing login.

**Cause:** Typically a cookie or session issue.

**Fix:**
1. Clear the browser cookies for both your Velora domain and Okta domain.
2. Ensure Velora is running on HTTPS (cookies require `Secure` flag).
3. Verify that the Velora domain and the redirect URI domain match exactly.
4. Check that third-party cookies are not blocked if Velora and Okta are on different domains.

---

## 9. Security Considerations

### Token Storage

- Velora stores OIDC tokens server-side in encrypted session storage. Tokens are never exposed to the browser.
- SAML assertions are validated and discarded after processing. Only the extracted claims are stored in the session.

### Client Secret Handling

- The Client Secret is encrypted at rest using AES-256-GCM.
- It is never displayed in the UI after initial configuration (masked with asterisks).
- Rotate the Client Secret periodically (recommended: every 90 days). Update in both Okta and Velora simultaneously.

### Redirect URI Validation

- Velora performs strict redirect URI matching. Wildcards are not supported.
- Only HTTPS redirect URIs are accepted in production mode.

### Session Lifetime

- SSO sessions in Velora respect the token lifetime configured in Okta.
- Configure Okta session policies under **Security** > **Authentication** > **Sign On Policy** in Okta Admin.
- Recommended: Set maximum session duration to 8 hours for standard users, 1 hour for administrators.

### Multi-Factor Authentication (MFA)

- MFA is enforced at the Okta level, not in Velora. Configure MFA policies in Okta under **Security** > **Multifactor**.
- Velora honors Okta's `amr` (Authentication Methods References) claim to verify MFA was completed.
- Recommended: Require MFA for all users accessing Velora, especially those with Risk Manager or Platform Administrator roles.

### PKCE (Proof Key for Code Exchange)

- Velora supports PKCE for OIDC flows. This is enabled by default and adds an additional layer of security against authorization code interception.
- Do not disable PKCE unless you have a specific technical reason.

### Certificate Pinning (SAML)

- Velora validates SAML assertions against the configured X.509 certificate.
- Enable **Strict Certificate Validation** in Velora SSO settings to reject assertions signed with an unknown certificate.

### Audit Logging

- All SSO authentication events are logged in Velora's audit log, including:
  - Successful logins (user, time, IP, IdP, role assigned).
  - Failed logins (reason, user if identifiable, IP).
  - JIT provisioning events (user created, role assigned).
  - Role changes from group mapping updates.
- Access audit logs at **Admin** > **Audit Log** > filter by "Authentication."

### Network Restrictions

- Configure IP allowlists in Okta to restrict where SSO authentication can originate.
- In Velora, you can restrict SSO login to specific network ranges under **Admin** > **Security** > **Network Policies**.

---

*Document maintained by the Velora TPRM platform team. For support, contact your Velora administrator or open a ticket in your internal IT service management system.*
