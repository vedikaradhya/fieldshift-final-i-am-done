import { test, expect } from '@playwright/test';

test.describe('Climate Data Display', () => {
  test.beforeEach(async ({ page }) => {
    // Skip authentication for now - test UI components directly
    // This is a temporary measure until backend stability is improved
    await page.goto('/');
  });

  test('displays climate section', async ({ page }) => {
    await expect(page.locator('text=Climate')).toBeVisible({ timeout: 10000 });
  });

  test('shows temperature data', async ({ page }) => {
    await expect(page.locator('text=Temperature')).toBeVisible({ timeout: 10000 });
    const tempElement = page.locator('.temperature-value');
    await expect(tempElement).toBeVisible();
  });

  test('shows rainfall data', async ({ page }) => {
    await expect(page.locator('text=Rainfall')).toBeVisible({ timeout: 10000 });
    const rainfallElement = page.locator('.rainfall-value');
    await expect(rainfallElement).toBeVisible();
  });

  test('shows soil moisture data', async ({ page }) => {
    await expect(page.locator('text=Soil moisture')).toBeVisible({ timeout: 10000 });
    const moistureElement = page.locator('.moisture-value');
    await expect(moistureElement).toBeVisible();
  });

  test('displays data source information', async ({ page }) => {
    await expect(page.locator('text=Source')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=AgriSpace simulated dataset')).toBeVisible();
  });

  test('shows simulated data warning', async ({ page }) => {
    await expect(page.locator('text=simulated')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Not a NASA measurement')).toBeVisible();
  });

  test('displays date information', async ({ page }) => {
    await expect(page.locator('text=Date')).toBeVisible({ timeout: 10000 });
    const dateElement = page.locator('.date-value');
    await expect(dateElement).toBeVisible();
  });

  test('climate data has valid numeric values', async ({ page }) => {
    await expect(page.locator('.temperature-value')).toBeVisible({ timeout: 10000 });
    
    const tempText = await page.locator('.temperature-value').textContent();
    const tempValue = parseFloat(tempText || '0');
    expect(tempValue).toBeGreaterThan(-50);
    expect(tempValue).toBeLessThan(60);
  });

  test('displays multiple climate metrics together', async ({ page }) => {
    await expect(page.locator('.climate-section')).toBeVisible({ timeout: 10000 });
    
    // Check that all key metrics are present
    await expect(page.locator('text=Temperature')).toBeVisible();
    await expect(page.locator('text=Rainfall')).toBeVisible();
    await expect(page.locator('text=Soil moisture')).toBeVisible();
    await expect(page.locator('text=Humidity')).toBeVisible();
  });
});
