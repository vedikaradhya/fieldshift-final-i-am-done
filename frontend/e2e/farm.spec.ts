import { test, expect } from '@playwright/test';

test.describe('Farm Management', () => {
  test.beforeEach(async ({ page }) => {
    // Skip authentication for now - test UI components directly
    // This is a temporary measure until backend stability is improved
    await page.goto('/');
  });

  test('displays dashboard with empty state', async ({ page }) => {
    await expect(page.locator('.app-shell')).toBeVisible();
    await expect(page.locator('text=Your farms')).toBeVisible();
    await expect(page.locator('text=No farms yet')).toBeVisible();
  });

  test('adds a demo farm successfully', async ({ page }) => {
    await page.click('button:has-text("Add demo farm")');
    
    // Wait for success message
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Verify farm appears in list
    await expect(page.locator('.farm-list')).toBeVisible();
    await expect(page.locator('text=Orchard North')).toBeVisible();
  });

  test('displays farm details after adding', async ({ page }) => {
    await page.click('button:has-text("Add demo farm")');
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Check for farm metrics
    await expect(page.locator('text=Total area')).toBeVisible();
    await expect(page.locator('text=hectares')).toBeVisible();
  });

  test('selects a farm from the list', async ({ page }) => {
    await page.click('button:has-text("Add demo farm")');
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Click on the farm in the list
    await page.click('.farm-list button');
    
    // Verify selection
    await expect(page.locator('.selected-farm')).toBeVisible();
  });

  test('displays climate data for selected farm', async ({ page }) => {
    await page.click('button:has-text("Add demo farm")');
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Wait for climate data to load
    await expect(page.locator('text=Climate')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Temperature')).toBeVisible();
    await expect(page.locator('text=Rainfall')).toBeVisible();
    await expect(page.locator('text=Soil moisture')).toBeVisible();
  });

  test('shows simulated data warning', async ({ page }) => {
    await page.click('button:has-text("Add demo farm")');
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Check for simulated data warning
    await expect(page.locator('text=simulated')).toBeVisible();
  });

  test('displays multiple farms', async ({ page }) => {
    // Add first farm
    await page.click('button:has-text("Add demo farm")');
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Add second farm (by clicking the button again)
    await page.click('button:has-text("Add demo farm")');
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Verify multiple farms in list
    const farmButtons = await page.locator('.farm-list button').count();
    expect(farmButtons).toBeGreaterThan(1);
  });

  test('updates total area when farms are added', async ({ page }) => {
    // Get initial total area (should be 0)
    const initialArea = await page.locator('.total-area').textContent();
    
    // Add farm
    await page.click('button:has-text("Add demo farm")');
    await expect(page.locator('.status')).toContainText('Farm saved', { timeout: 10000 });
    
    // Check that total area increased
    const newArea = await page.locator('.total-area').textContent();
    expect(newArea).not.toBe(initialArea);
    expect(parseFloat(newArea || '0')).toBeGreaterThan(0);
  });
});
