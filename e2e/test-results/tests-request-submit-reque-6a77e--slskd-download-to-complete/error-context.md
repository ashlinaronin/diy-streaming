# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests/request.spec.js >> submit request and wait for slskd download to complete
- Location: tests/request.spec.js:5:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.waitForTimeout: Test timeout of 30000ms exceeded.
```

# Page snapshot

```yaml
- generic [active] [ref=f1e1]:
  - heading "Request Status" [level=1] [ref=f1e2]
  - paragraph [ref=f1e3]:
    - link "New requests" [ref=f1e4] [cursor=pointer]:
      - /url: /request/
  - table [ref=f1e5]:
    - rowgroup [ref=f1e6]:
      - row [ref=f1e7]:
        - columnheader "ID" [ref=f1e8]
        - columnheader "Line" [ref=f1e9]
        - columnheader "Artist" [ref=f1e10]
        - columnheader "Album" [ref=f1e11]
        - columnheader "Status" [ref=f1e12]
        - columnheader "Result" [ref=f1e13]
        - columnheader "Error" [ref=f1e14]
    - rowgroup [ref=f1e15]:
      - row [ref=f1e16]:
        - cell "12" [ref=f1e17]
        - cell "Mocked Artist - Mocked Album" [ref=f1e18]
        - cell "Mocked Artist" [ref=f1e19]
        - cell "Mocked Album" [ref=f1e20]
        - cell "queued" [ref=f1e21]
        - cell "None" [ref=f1e22]
        - cell "None" [ref=f1e23]
      - row [ref=f1e24]:
        - cell "11" [ref=f1e25]
        - cell "Direct Test - Album" [ref=f1e26]
        - cell "Direct Test" [ref=f1e27]
        - cell "Album" [ref=f1e28]
        - cell "failed" [ref=f1e29]
        - cell "None" [ref=f1e30]
        - 'cell "slskd search error: 404 Client Error: Not Found for url: http://slskd:5030/api/search?q=Direct+Test+Album" [ref=f1e31]'
      - row [ref=f1e32]:
        - cell "10" [ref=f1e33]
        - cell "Foo - Bar" [ref=f1e34]
        - cell "Foo" [ref=f1e35]
        - cell "Bar" [ref=f1e36]
        - cell "completed" [ref=f1e37]
        - cell "/music/Foo Bar - mock.flac" [ref=f1e38]
        - cell "None" [ref=f1e39]
      - row [ref=f1e40]:
        - cell "9" [ref=f1e41]
        - cell "Mocked Artist - Mocked Album" [ref=f1e42]
        - cell "Mocked Artist" [ref=f1e43]
        - cell "Mocked Album" [ref=f1e44]
        - cell "completed" [ref=f1e45]
        - cell "/music/Mocked Artist Mocked Album - mock.flac" [ref=f1e46]
        - cell "None" [ref=f1e47]
      - row [ref=f1e48]:
        - cell "8" [ref=f1e49]
        - cell "Mocked Artist - Mocked Album" [ref=f1e50]
        - cell "Mocked Artist" [ref=f1e51]
        - cell "Mocked Album" [ref=f1e52]
        - cell "completed" [ref=f1e53]
        - cell "/music/Mocked Artist Mocked Album - mock.flac" [ref=f1e54]
        - cell "None" [ref=f1e55]
      - row [ref=f1e56]:
        - cell "7" [ref=f1e57]
        - cell "Mocked Artist - Mocked Album" [ref=f1e58]
        - cell "Mocked Artist" [ref=f1e59]
        - cell "Mocked Album" [ref=f1e60]
        - cell "completed" [ref=f1e61]
        - cell "/music/Mocked Artist Mocked Album - mock.flac" [ref=f1e62]
        - cell "None" [ref=f1e63]
      - row [ref=f1e64]:
        - cell "6" [ref=f1e65]
        - cell "Mocked Artist - Mocked Album" [ref=f1e66]
        - cell "Mocked Artist" [ref=f1e67]
        - cell "Mocked Album" [ref=f1e68]
        - cell "downloading" [ref=f1e69]
        - 'cell "{''bitrate'': 0, ''filename'': ''Mocked - Artist Mocked Album.flac'', ''format'': ''flac'', ''id'': ''mock-1786577134246''}" [ref=f1e70]'
        - cell "None" [ref=f1e71]
      - row [ref=f1e72]:
        - cell "5" [ref=f1e73]
        - cell "Mocked Artist - Mocked Album" [ref=f1e74]
        - cell "Mocked Artist" [ref=f1e75]
        - cell "Mocked Album" [ref=f1e76]
        - cell "failed" [ref=f1e77]
        - cell "None" [ref=f1e78]
        - cell "'list' object has no attribute 'get'" [ref=f1e79]
      - row [ref=f1e80]:
        - cell "4" [ref=f1e81]
        - cell "Mocked Artist - Mocked Album" [ref=f1e82]
        - cell "Mocked Artist" [ref=f1e83]
        - cell "Mocked Album" [ref=f1e84]
        - cell "failed" [ref=f1e85]
        - cell "None" [ref=f1e86]
        - 'cell "slskd search error: 404 Client Error: Not Found for url: http://slskd:5030/api/search?q=Mocked+Artist+Mocked+Album" [ref=f1e87]'
      - row [ref=f1e88]:
        - cell "3" [ref=f1e89]
        - cell "E2E Test Artist - E2E Test Album" [ref=f1e90]
        - cell "E2E Test Artist" [ref=f1e91]
        - cell "E2E Test Album" [ref=f1e92]
        - cell "failed" [ref=f1e93]
        - cell "None" [ref=f1e94]
        - 'cell "slskd search error: 404 Client Error: Not Found for url: http://slskd:5030/api/search?q=E2E+Test+Artist+E2E+Test+Album" [ref=f1e95]'
      - row [ref=f1e96]:
        - cell "2" [ref=f1e97]
        - cell "Test Artist - Test Album" [ref=f1e98]
        - cell "Test Artist" [ref=f1e99]
        - cell "Test Album" [ref=f1e100]
        - cell "failed" [ref=f1e101]
        - cell "None" [ref=f1e102]
        - 'cell "slskd search error: 404 Client Error: Not Found for url: http://slskd:5030/api/search?q=Test+Artist+Test+Album" [ref=f1e103]'
      - row [ref=f1e104]:
        - cell "1" [ref=f1e105]
        - cell "Test Artist - Test Album" [ref=f1e106]
        - cell "Test Artist" [ref=f1e107]
        - cell "Test Album" [ref=f1e108]
        - cell "failed" [ref=f1e109]
        - cell "None" [ref=f1e110]
        - 'cell "slskd search error: HTTPConnectionPool(host=''slskd'', port=5030): Max retries exceeded with url: /api/search?q=Test+Artist+Test+Album (Caused by NameResolutionError(\"HTTPConnection(host=''slskd'', port=5030): Failed to resolve ''slskd'' ([Errno -2] Name or service not known)\"))" [ref=f1e111]'
```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  | const fs = require('fs');
  3  | const path = require('path');
  4  | 
  5  | test('submit request and wait for slskd download to complete', async ({ page }) => {
  6  |   await page.goto('/');
  7  |   await page.fill('textarea[name="requests"]', 'Mocked Artist - Mocked Album');
  8  |   await page.click('button[type=submit]');
  9  |   await page.waitForURL('**/status');
  10 | 
  11 |   // Find the row for our submitted line
  12 |   const row = page.locator('tbody tr', { hasText: 'Mocked Artist - Mocked Album' }).first();
  13 | 
  14 |   // Poll for up to 60s for the job status to become 'completed' or 'failed'
  15 |   const statusCell = row.locator('td').nth(4);
  16 |   let statusText = '';
  17 |   const maxRetries = 30; // 30 * 2s = 60s
  18 |   for (let i = 0; i < maxRetries; i++) {
  19 |     statusText = (await statusCell.innerText()).trim();
  20 |     if (statusText === 'completed' || statusText === 'failed') break;
> 21 |     await page.waitForTimeout(2000);
     |                ^ Error: page.waitForTimeout: Test timeout of 30000ms exceeded.
  22 |   }
  23 |   expect(['completed', 'failed'].includes(statusText)).toBeTruthy();
  24 | 
  25 |   if (statusText === 'completed') {
  26 |     // Get result path from result column
  27 |     const resultCell = row.locator('td').nth(5);
  28 |     const resultText = (await resultCell.innerText()).trim();
  29 | 
  30 |     // Extract filename and check it exists under workspace music directory
  31 |     const filename = path.basename(resultText);
  32 |     const musicDir = path.resolve(__dirname, '..', '..', 'music');
  33 |     const filepath = path.join(musicDir, filename);
  34 |     const exists = fs.existsSync(filepath);
  35 |     expect(exists).toBeTruthy();
  36 |   } else {
  37 |     // If failed, surface the error cell for debugging
  38 |     const err = await row.locator('td').nth(6).innerText();
  39 |     throw new Error('Job failed: ' + err);
  40 |   }
  41 | });
  42 | 
```