# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: farm.spec.ts >> Farm Management >> displays dashboard with empty state
- Location: e2e/farm.spec.ts:10:3

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
Call log:
  - navigating to "http://localhost:5173/", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Farm Management', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     // Skip authentication for now - test UI components directly
  6  |     // This is a temporary measure until backend stability is improved
> 7  |     await page.goto('/');
     |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
  8  |   });
  9  | 
  10 |   test('displays dashboard with empty state', async ({ page }) => {
  11 |     await expect(page.locator('.app-shell')).toBeVisible();
  12 |     await expect(page.locator('text=Your farms')).toBeVisible();
  13 |     await expect(page.locator('text=No farms yet')).toBeVisible();
  14 |   });
  15 | 
  16 |   test('adds a demo farm successfully', async ({ page }) => {
  17 |     await page.click('button:has-text("Add demo farm")');
  18 |     
  19 |     // Wait for success message
  20 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  21 |     
  22 |     // Verify farm appears in list
  23 |     await expect(page.locator('.farm-list')).toBeVisible();
  24 |     await expect(page.locator('text=Orchard North')).toBeVisible();
  25 |   });
  26 | 
  27 |   test('displays farm details after adding', async ({ page }) => {
  28 |     await page.click('button:has-text("Add demo farm")');
  29 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  30 |     
  31 |     // Check for farm metrics
  32 |     await expect(page.locator('text=Total area')).toBeVisible();
  33 |     await expect(page.locator('text=hectares')).toBeVisible();
  34 |   });
  35 | 
  36 |   test('selects a farm from the list', async ({ page }) => {
  37 |     await page.click('button:has-text("Add demo farm")');
  38 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  39 |     
  40 |     // Click on the farm in the list
  41 |     await page.click('.farm-list button');
  42 |     
  43 |     // Verify selection
  44 |     await expect(page.locator('.selected-farm')).toBeVisible();
  45 |   });
  46 | 
  47 |   test('displays climate data for selected farm', async ({ page }) => {
  48 |     await page.click('button:has-text("Add demo farm")');
  49 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  50 |     
  51 |     // Wait for climate data to load
  52 |     await expect(page.locator('text=Climate')).toBeVisible({ timeout: 10000 });
  53 |     await expect(page.locator('text=Temperature')).toBeVisible();
  54 |     await expect(page.locator('text=Rainfall')).toBeVisible();
  55 |     await expect(page.locator('text=Soil moisture')).toBeVisible();
  56 |   });
  57 | 
  58 |   test('shows simulated data warning', async ({ page }) => {
  59 |     await page.click('button:has-text("Add demo farm")');
  60 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  61 |     
  62 |     // Check for simulated data warning
  63 |     await expect(page.locator('text=simulated')).toBeVisible();
  64 |   });
  65 | 
  66 |   test('displays multiple farms', async ({ page }) => {
  67 |     // Add first farm
  68 |     await page.click('button:has-text("Add demo farm")');
  69 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  70 |     
  71 |     // Add second farm (by clicking the button again)
  72 |     await page.click('button:has-text("Add demo farm")');
  73 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  74 |     
  75 |     // Verify multiple farms in list
  76 |     const farmButtons = await page.locator('.farm-list button').count();
  77 |     expect(farmButtons).toBeGreaterThan(1);
  78 |   });
  79 | 
  80 |   test('updates total area when farms are added', async ({ page }) => {
  81 |     // Get initial total area (should be 0)
  82 |     const initialArea = await page.locator('.total-area').textContent();
  83 |     
  84 |     // Add farm
  85 |     await page.click('button:has-text("Add demo farm")');
  86 |     await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
  87 |     
  88 |     // Check that total area increased
  89 |     const newArea = await page.locator('.total-area').textContent();
  90 |     expect(newArea).not.toBe(initialArea);
  91 |     expect(parseFloat(newArea || '0')).toBeGreaterThan(0);
  92 |   });
  93 | });
  94 | 
```