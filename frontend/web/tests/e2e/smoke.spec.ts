import { test, expect } from "@playwright/test";

/**
 * Velora TPRM v2.1 — E2E Smoke Tests (with real login)
 *
 * Headless Chromium: hits every route, checks for:
 * - No 500 errors
 * - No console TypeErrors/ReferenceErrors
 * - Page renders actual content (not just login redirect)
 * - Screenshots captured for manual visual review
 */

const PUBLIC_ROUTES = [
  { path: "/login", name: "Login" },
];

const PORTAL_ROUTES = [
  { path: "/portal", name: "Portal Dashboard" },
  { path: "/portal/assessments", name: "Portal Assessments" },
  { path: "/portal/evidence", name: "Portal Evidence" },
  { path: "/portal/findings", name: "Portal Findings" },
];

const DASHBOARD_ROUTES = [
  { path: "/dashboard", name: "Dashboard" },
  { path: "/vendors", name: "Vendors" },
  { path: "/assessments", name: "Assessments" },
  { path: "/frameworks", name: "Frameworks" },
  { path: "/findings", name: "Findings" },
  { path: "/monitoring", name: "Monitoring" },
  { path: "/evidence", name: "Evidence" },
  { path: "/reports", name: "Reports" },
  { path: "/admin/users", name: "Admin Users" },
  { path: "/admin/roles", name: "Admin Roles" },
  { path: "/admin/integrations", name: "Admin Integrations" },
  { path: "/admin/settings", name: "Admin Settings" },
];

// Helper to login and set tokens in localStorage
async function loginAndSetTokens(page: any) {
  // Call login API directly to get tokens
  const loginResp = await page.request.post("http://localhost:8000/api/v1/auth/login", {
    data: { email: "admin@velora-demo.com", password: "admin123" },
  });
  const tokens = await loginResp.json();

  if (!tokens.access_token) {
    throw new Error(`Login failed: ${JSON.stringify(tokens)}`);
  }

  // Set tokens in localStorage before navigating
  await page.goto("/login", { waitUntil: "domcontentloaded" });
  await page.evaluate((t: any) => {
    localStorage.setItem("access_token", t.access_token);
    localStorage.setItem("refresh_token", t.refresh_token);
  }, tokens);
}

test.describe("Public Routes — No Auth Required", () => {
  for (const route of PUBLIC_ROUTES) {
    test(`${route.name} (${route.path}) loads without 500`, async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (err: Error) => errors.push(err.message));

      const resp = await page.goto(route.path, { waitUntil: "domcontentloaded" });
      expect(resp?.status()).not.toBe(500);

      await page.screenshot({
        path: `tests/e2e/results/${route.name.toLowerCase().replace(/\s/g, "-")}.png`,
        fullPage: true,
      });

      const jsErrors = errors.filter(
        (e) => e.includes("TypeError") || e.includes("ReferenceError") || e.includes("Cannot read")
      );
      expect(jsErrors, `JS errors on ${route.path}`).toHaveLength(0);
    });
  }
});

test.describe("Portal Routes — Vendor Facing", () => {
  for (const route of PORTAL_ROUTES) {
    test(`${route.name} (${route.path}) loads without 500`, async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (err: Error) => errors.push(err.message));

      const resp = await page.goto(route.path, { waitUntil: "domcontentloaded" });
      expect(resp?.status()).not.toBe(500);

      await page.screenshot({
        path: `tests/e2e/results/${route.name.toLowerCase().replace(/\s/g, "-")}.png`,
        fullPage: true,
      });

      const jsErrors = errors.filter(
        (e) => e.includes("TypeError") || e.includes("ReferenceError") || e.includes("Cannot read")
      );
      expect(jsErrors, `JS errors on ${route.path}`).toHaveLength(0);
    });
  }
});

test.describe("Dashboard Routes — Authenticated", () => {
  test.beforeEach(async ({ page }) => {
    await loginAndSetTokens(page);
  });

  for (const route of DASHBOARD_ROUTES) {
    test(`${route.name} (${route.path}) loads with data`, async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (err: Error) => errors.push(err.message));

      await page.goto(route.path, { waitUntil: "networkidle" });

      // Wait for page to fully render
      await page.waitForTimeout(3000);

      // Verify we're NOT on the login page (auth worked)
      const url = page.url();
      const onLoginPage = url.includes("/login");

      await page.screenshot({
        path: `tests/e2e/results/${route.name.toLowerCase().replace(/\s/g, "-")}.png`,
        fullPage: true,
      });

      // Check for JS runtime errors
      const jsErrors = errors.filter(
        (e) =>
          e.includes("TypeError") ||
          e.includes("ReferenceError") ||
          e.includes("Cannot read") ||
          e.includes("is not a function") ||
          e.includes("is not defined")
      );
      expect(jsErrors, `JS errors on ${route.path}: ${jsErrors.join("; ")}`).toHaveLength(0);

      // Verify we actually loaded the page, not login redirect
      expect(onLoginPage, `${route.path} redirected to login — auth failed`).toBe(false);
    });
  }
});

test.describe("Build Verification", () => {
  test("Root redirect works (/ → /dashboard or /login)", async ({ page }) => {
    const resp = await page.goto("/", { waitUntil: "domcontentloaded" });
    expect(resp?.status()).not.toBe(500);
    const url = page.url();
    expect(url).toMatch(/\/(dashboard|login)/);
  });
});
