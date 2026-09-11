import { defineConfig, devices } from '@playwright/test'

const assistantSpec = /(?:offline-assistant-fallback|assistant-proposal)\.spec\.ts/
const offlinePwaSpec = /offline-vertical-slice\.spec\.ts/
const devSpecsToIgnore = [assistantSpec, offlinePwaSpec]

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  use: {
    baseURL: 'http://127.0.0.1:3000',
    locale: 'ru-RU',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      testIgnore: devSpecsToIgnore,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'webkit',
      testIgnore: devSpecsToIgnore,
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'assistant-chromium',
      testMatch: assistantSpec,
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://127.0.0.1:3001',
      },
    },
    {
      name: 'assistant-webkit',
      testMatch: assistantSpec,
      use: {
        ...devices['Desktop Safari'],
        baseURL: 'http://127.0.0.1:3001',
      },
    },
    {
      name: 'offline-pwa-chromium',
      testMatch: offlinePwaSpec,
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://127.0.0.1:3002',
      },
    },
    {
      name: 'offline-pwa-webkit',
      testMatch: offlinePwaSpec,
      use: {
        ...devices['Desktop Safari'],
        baseURL: 'http://127.0.0.1:3002',
      },
    },
  ],
  webServer: [
    {
      command: 'python ../api/run.py',
      cwd: '.',
      url: 'http://127.0.0.1:8000/docs',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: 'pnpm dev --host 127.0.0.1 --port 3000',
      cwd: '.',
      url: 'http://127.0.0.1:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: 'pnpm dev --host 127.0.0.1 --port 3001',
      cwd: '.',
      url: 'http://127.0.0.1:3001',
      env: {
        NUXT_PUBLIC_MIND_DETECTIVE_ARM: 'assistant',
      },
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: 'test -f .output/public/index.html || pnpm build; python -m http.server 3002 --bind 127.0.0.1 --directory .output/public',
      cwd: '.',
      url: 'http://127.0.0.1:3002',
      reuseExistingServer: !process.env.CI,
      timeout: 90_000,
    },
  ],
})
