/** @type {import('@playwright/test').PlaywrightTestConfig} */
module.exports = {
  use: {
    baseURL: 'http://localhost:5002',
    headless: true,
    ignoreHTTPSErrors: true,
    viewport: { width: 1280, height: 720 }
  }
};
