import { expect, test } from '@playwright/test'
import { caseFixture, journalEntry, seedCase, storedCase } from './helpers'

const legacyV1 = {
  schema: 'mind-detective-case/v1',
  case_id: 'legacy-import',
  item_label: 'паспорт',
  created_at: '2026-09-09T18:00:00Z',
  updated_at: '2026-09-09T18:05:00Z',
  lifecycle: 'active',
  statements: [],
  timeline: null,
  search_checks: [],
  candidates: [],
  next_action: null,
  constraints: [],
  outcome: null,
}

test('valid v1 import migrates locally to canonical v2 offline and future schema is rejected', async ({ page, context }) => {
  let validationRequests = 0
  await page.route('**/api/v1/case/validate', async (route) => {
    validationRequests += 1
    await route.abort('failed')
  })

  await page.goto('/')
  await expect(page.getByTestId('offline-route-ready')).toBeVisible()
  await context.setOffline(true)
  await page.getByTestId('case-import').setInputFiles({
    name: 'legacy.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(legacyV1)),
  })
  await expect(page).toHaveURL(/\/cases\/legacy-import/)
  const migrated = await storedCase(page, 'legacy-import')
  expect(migrated?.schema).toBe('mind-detective-case/v2')
  expect(migrated?.current_mode).toBe('unselected')
  expect(migrated?.interaction_journal).toEqual([])
  expect(migrated?.action_feedback).toEqual([])
  expect(validationRequests).toBe(0)

  await context.setOffline(false)
  await page.goto('/')
  await page.getByTestId('case-import').setInputFiles({
    name: 'future.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ schema: 'mind-detective-case/v999' })),
  })
  await expect(page.getByRole('status')).toContainText('не поддерживается')
  expect(validationRequests).toBe(0)
})

test('engaged case exposes durability warning install education and explicit JSON export', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'storage', {
      configurable: true,
      value: {
        persisted: async () => false,
        persist: async () => false,
      },
    })
  })
  const caseValue = caseFixture({
    interaction_journal: [journalEntry('search-1', 'search', 'Проверил куртку.')],
  })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('storage-notice')).toBeVisible()
  await expect(page.getByTestId('storage-notice')).toContainText('не гарантирует')
  await expect(page.getByTestId('install-education')).toBeVisible()
  await expect(page.getByTestId('case-data-actions')).toBeVisible()

  const downloadPromise = page.waitForEvent('download')
  await page.getByTestId('export-case').click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toContain(caseValue.case_id)
})
