# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication Flow >> successfully signs in with existing account
- Location: e2e/auth.spec.ts:89:3

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
Call log:
  - navigating to "http://localhost:5173/", waiting until "load"

```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('Authentication Flow', () => {
  4   |   test.beforeEach(async ({ page }) => {
> 5   |     await page.goto('/');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
  6   |   });
  7   | 
  8   |   test('displays landing page with auth buttons', async ({ page }) => {
  9   |     await expect(page.locator('.landing-nav')).toBeVisible();
  10  |     await expect(page.locator('.brand')).toContainText('AgriSpace');
  11  |     await expect(page.locator('button:has-text("Sign in")')).toBeVisible();
  12  |     await expect(page.locator('button:has-text("Create account")')).toBeVisible();
  13  |   });
  14  | 
  15  |   test('opens sign in modal', async ({ page }) => {
  16  |     await page.click('button:has-text("Sign in")');
  17  |     await expect(page.locator('.modal-overlay')).toBeVisible({ timeout: 5000 });
  18  |     await expect(page.locator('.modal-card')).toContainText('Sign in');
  19  |     await expect(page.locator('input[type="email"]')).toBeVisible();
  20  |     await expect(page.locator('input[type="password"]')).toBeVisible();
  21  |   });
  22  | 
  23  |   test('opens create account modal', async ({ page }) => {
  24  |     await page.click('button:has-text("Create account")');
  25  |     await expect(page.locator('.modal-overlay')).toBeVisible({ timeout: 5000 });
  26  |     await expect(page.locator('.modal-card')).toContainText('Create account');
  27  |     await expect(page.locator('input[type="text"]')).toBeVisible();
  28  |     await expect(page.locator('input[type="email"]')).toBeVisible();
  29  |     await expect(page.locator('input[type="password"]')).toBeVisible();
  30  |     await expect(page.locator('input[type="tel"]')).toBeVisible();
  31  |   });
  32  | 
  33  |   test('switches between sign in and create account', async ({ page }) => {
  34  |     await page.click('button:has-text("Sign in")');
  35  |     await page.click('.modal-switch:has-text("Create account")');
  36  |     await expect(page.locator('.modal-card')).toContainText('Create account');
  37  |     await page.click('.modal-switch:has-text("Sign in")');
  38  |     await expect(page.locator('.modal-card')).toContainText('Sign in');
  39  |   });
  40  | 
  41  |   test('closes modal when clicking close button', async ({ page }) => {
  42  |     await page.click('button:has-text("Sign in")');
  43  |     await page.click('.modal-close');
  44  |     await expect(page.locator('.modal-overlay')).not.toBeVisible({ timeout: 5000 });
  45  |   });
  46  | 
  47  |   test('closes modal when clicking overlay', async ({ page }) => {
  48  |     await page.click('button:has-text("Sign in")');
  49  |     await page.click('.modal-overlay');
  50  |     await expect(page.locator('.modal-overlay')).not.toBeVisible({ timeout: 5000 });
  51  |   });
  52  | 
  53  |   test('shows validation error for weak password during registration', async ({ page }) => {
  54  |     await page.click('button:has-text("Create account")');
  55  |     await page.fill('input[type="text"]', 'Test User');
  56  |     await page.fill('input[type="email"]', `test${Date.now()}@example.com`);
  57  |     await page.fill('input[type="password"]', 'weak');
  58  |     await page.click('button.primary.full-width');
  59  |     await expect(page.locator('.status')).toBeVisible();
  60  |     const statusText = await page.locator('.status').textContent();
  61  |     expect(statusText).toContain('at least 12 characters');
  62  |   });
  63  | 
  64  |   test('successfully registers a new account', async ({ page }) => {
  65  |     const timestamp = Date.now();
  66  |     const email = `e2e-test-${timestamp}@example.com`;
  67  |     const password = 'TestPassword123';
  68  |     
  69  |     await page.click('button:has-text("Create account")');
  70  |     await page.fill('input[type="text"]', 'E2E Test User');
  71  |     await page.fill('input[type="email"]', email);
  72  |     await page.fill('input[type="password"]', password);
  73  |     await page.fill('input[type="tel"]', '1234567890');
  74  |     await page.click('button.primary.full-width');
  75  |     
  76  |     // Wait for status message
  77  |     await expect(page.locator('.status')).toBeVisible({ timeout: 15000 });
  78  |     const statusText = await page.locator('.status').textContent();
  79  |     
  80  |     // Check for success message or error
  81  |     if (statusText && statusText.includes('Welcome to AgriSpace')) {
  82  |       await expect(page.locator('.app-shell')).toBeVisible({ timeout: 5000 });
  83  |     } else {
  84  |       // If registration fails, that's okay for this test - we're testing the UI flow
  85  |       console.log('Registration response:', statusText);
  86  |     }
  87  |   });
  88  | 
  89  |   test('successfully signs in with existing account', async ({ page }) => {
  90  |     // First register
  91  |     const timestamp = Date.now();
  92  |     const email = `e2e-login-${timestamp}@example.com`;
  93  |     const password = 'TestPassword123';
  94  |     
  95  |     await page.click('button:has-text("Create account")');
  96  |     await page.fill('input[type="text"]', 'Login Test User');
  97  |     await page.fill('input[type="email"]', email);
  98  |     await page.fill('input[type="password"]', password);
  99  |     await page.fill('input[type="tel"]', '1234567890');
  100 |     await page.click('button.primary.full-width');
  101 |     await expect(page.locator('.app-shell')).toBeVisible({ timeout: 15000 });
  102 |     
  103 |     // Logout by clearing localStorage
  104 |     await page.evaluate(() => localStorage.removeItem('agrispace-token'));
  105 |     await page.reload();
```