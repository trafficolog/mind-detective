import { defineConfig, devices } from '@playwright/test'

// Post-deploy smoke test of a published static build (GitHub Pages or any host).
// Usage: SMOKE_BASE_URL=https://<owner>.github.io/<repo>/ pnpm exec playwright test -c playwright.smoke.config.ts
// No local servers are started: the test only reads the deployed site and writes to the
// test browser's own IndexedDB.
const raw = process.env.SMOKE_BASE_URL
if (!raw) throw new Error('SMOKE_BASE_URL is required, e.g. https://owner.github.io/repo/')
const baseURL = raw.endsWith('/') ? raw : `${raw}/`

export default defineConfig({
  testDir: './tests/smoke',
  fullyParallel: false,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  timeout: 60_000,
  use: {
    baseURL,
    locale: 'ru-RU',
    trace: 'retain-on-failure',
    ignoreHTTPSErrors: Boolean(process.env.SMOKE_IGNORE_HTTPS_ERRORS),
  },
  projects: [
    { name: 'smoke-android-chromium', use: { ...devices['Pixel 7'] } },
    { name: 'smoke-iphone-webkit', use: { ...devices['iPhone 14'] } },
  ],
})
