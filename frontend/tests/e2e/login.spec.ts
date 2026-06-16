import { expect, test } from "@playwright/test";

test("login page renders Script9 logo and 3D cube", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator(".cube-container")).toBeVisible();
  await expect(page.locator(".logo-script9")).toBeVisible();
  await expect(page.locator("button:has-text('Continuar con Google')")).toBeVisible();
});
