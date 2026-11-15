# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: climate.spec.ts >> Climate Data Display >> climate data has valid numeric values
- Location: e2e/climate.spec.ts:48:3

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
  3  | test.describe('Climate Data Display', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     // Skip authentication for now - test UI components directly
  6  |     // This is a temporary measure until backend stability is improved
> 7  |     await page.goto('/');
     |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:5173/
  8  |   });
  9  | 
  10 |   test('displays climate section', async ({ page }) => {
  11 |     await expect(page.locator('text=Climate')).toBeVisible({ timeout: 10000 });
  12 |   });
  13 | 
  14 |   test('shows temperature data', async ({ page }) => {
  15 |     await expect(page.locator('text=Temperature')).toBeVisible({ timeout: 10000 });
  16 |     const tempElement = page.locator('.temperature-value');
  17 |     await expect(tempElement).toBeVisible();
  18 |   });
  19 | 
  20 |   test('shows rainfall data', async ({ page }) => {
  21 |     await expect(page.locator('text=Rainfall')).toBeVisible({ timeout: 10000 });
  22 |     const rainfallElement = page.locator('.rainfall-value');
  23 |     await expect(rainfallElement).toBeVisible();
  24 |   });
  25 | 
  26 |   test('shows soil moisture data', async ({ page }) => {
  27 |     await expect(page.locator('text=Soil moisture')).toBeVisible({ timeout: 10000 });
  28 |     const moistureElement = page.locator('.moisture-value');
  29 |     await expect(moistureElement).toBeVisible();
  30 |   });
  31 | 
  32 |   test('displays data source information', async ({ page }) => {
  33 |     await expect(page.locator('text=Source')).toBeVisible({ timeout: 10000 });
  34 |     await expect(page.locator('text=AgriSpace simulated dataset')).toBeVisible();
  35 |   });
  36 | 
  37 |   test('shows simulated data warning', async ({ page }) => {
  38 |     await expect(page.locator('text=simulated')).toBeVisible({ timeout: 10000 });
  39 |     await expect(page.locator('text=Not a NASA measurement')).toBeVisible();
  40 |   });
  41 | 
  42 |   test('displays date information', async ({ page }) => {
  43 |     await expect(page.locator('text=Date')).toBeVisible({ timeout: 10000 });
  44 |     const dateElement = page.locator('.date-value');
  45 |     await expect(dateElement).toBeVisible();
  46 |   });
  47 | 
  48 |   test('climate data has valid numeric values', async ({ page }) => {
  49 |     await expect(page.locator('.temperature-value')).toBeVisible({ timeout: 10000 });
  50 |     
  51 |     const tempText = await page.locator('.temperature-value').textContent();
  52 |     const tempValue = parseFloat(tempText || '0');
  53 |     expect(tempValue).toBeGreaterThan(-50);
  54 |     expect(tempValue).toBeLessThan(60);
  55 |   });
  56 | 
  57 |   test('displays multiple climate metrics together', async ({ page }) => {
  58 |     await expect(page.locator('.climate-section')).toBeVisible({ timeout: 10000 });
  59 |     
  60 |     // Check that all key metrics are present
  61 |     await expect(page.locator('text=Temperature')).toBeVisible();
  62 |     await expect(page.locator('text=Rainfall')).toBeVisible();
  63 |     await expect(page.locator('text=Soil moisture')).toBeVisible();
  64 |     await expect(page.locator('text=Humidity')).toBeVisible();
  65 |   });
  66 | });
  67 | 
```