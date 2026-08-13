const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test('submit request and wait for slskd download to complete', async ({ page }) => {
  await page.goto('/');
  // submit as a free-form search line (no dash required)
  await page.fill('textarea[name="requests"]', 'Mocked Artist Mocked Album');
  await page.click('button[type=submit]');
  await page.waitForURL('**/status');

  // Find the row for our submitted line
  const row = page.locator('tbody tr', { hasText: 'Mocked Artist - Mocked Album' }).first();

  // Poll for up to 60s for the job status to become 'completed' or 'failed'
  const statusCell = row.locator('td').nth(4);
  let statusText = '';
  const maxRetries = 30; // 30 * 2s = 60s
  for (let i = 0; i < maxRetries; i++) {
    statusText = (await statusCell.innerText()).trim();
    if (statusText === 'completed' || statusText === 'failed') break;
    await page.waitForTimeout(2000);
  }
  expect(['completed', 'failed'].includes(statusText)).toBeTruthy();

  if (statusText === 'completed') {
    // Get result path from result column
    const resultCell = row.locator('td').nth(5);
    const resultText = (await resultCell.innerText()).trim();

    // Extract filename and check it exists under workspace music directory
    const filename = path.basename(resultText);
    const musicDir = path.resolve(__dirname, '..', '..', 'music');
    const filepath = path.join(musicDir, filename);
    const exists = fs.existsSync(filepath);
    expect(exists).toBeTruthy();
  } else {
    // If failed, surface the error cell for debugging
    const err = await row.locator('td').nth(6).innerText();
    throw new Error('Job failed: ' + err);
  }
});
