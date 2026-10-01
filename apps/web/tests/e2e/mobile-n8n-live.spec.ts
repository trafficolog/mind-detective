import { expect, test } from '@playwright/test'
import { addZone, createMobileCase, onboarded } from './mobileHelpers'

// Opt-in check against a real n8n instance with the workflow from integrations/n8n imported:
//   MD_E2E_N8N_URL=http://localhost:5678 MD_E2E_N8N_TOKEN=<token> pnpm exec playwright test mobile-n8n-live --project=chromium
const N8N_URL = process.env.MD_E2E_N8N_URL ?? ''
const N8N_TOKEN = process.env.MD_E2E_N8N_TOKEN ?? ''

test.skip(!N8N_URL, 'MD_E2E_N8N_URL is not set')
test.use({
  viewport: { width: 430, height: 844 },
  permissions: ['microphone'],
  launchOptions: {
    executablePath: process.env.MD_E2E_CHROMIUM_EXECUTABLE || undefined,
    args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'],
  },
})

test('live n8n: md-propose answer passes the guard and md-transcribe fills the field', async ({ page }) => {
  await onboarded(page, {
    'md.mobile.assistant': '1',
    'md.mobile.server': JSON.stringify({ url: N8N_URL, token: N8N_TOKEN }),
  })
  await createMobileCase(page, 'Ключи', 'physical', 'search')
  await addZone(page, 'Сумка')

  await page.getByTestId('assistant-ask').click()
  await expect(page.getByTestId('assistant-proposal')).toBeVisible({ timeout: 15_000 })
  await expect(page.getByTestId('assistant-proposal')).toHaveAttribute('data-source', 'assistant')

  await page.getByTestId('check-now').click()
  const dictate = page.getByRole('dialog').getByRole('button', { name: 'Надиктовать' })
  await dictate.click()
  await expect(page.getByRole('dialog').getByRole('button', { name: 'Остановить' })).toBeVisible()
  await page.waitForTimeout(1200)
  await page.getByRole('dialog').getByRole('button', { name: 'Остановить' }).click()
  await expect(page.locator('#check-note')).not.toHaveValue('', { timeout: 15_000 })
})
