import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { expect, test } from '@playwright/test'
import { candidate, caseFixture, journalEntry, searchCheck, seedCase } from './helpers'

test('journal provenance partial accessibility and persistent summary survive in one shell', async ({ page }) => {
  const partial = {
    ...searchCheck('check-partial', 'candidate-1', 'карманы куртки', 'reported_check'),
    result: 'partial' as const,
    inaccessible_parts: ['внутренний карман'],
  }
  const caseValue = caseFixture({
    candidates: [candidate('candidate-1', 'карманы куртки', 'partial')],
    search_checks: [partial],
    interaction_journal: [
      journalEntry('recon-entry', 'reconstruction', 'Я вошёл домой после прогулки.'),
      journalEntry('search-entry', 'search', 'Проверил верхнюю одежду.'),
      journalEntry('system-entry', 'system', 'Безопасный системный шаг.'),
    ],
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('case-shell')).toBeVisible()
  await expect(page.getByTestId('progress-strip')).toBeVisible()
  await expect(page.getByTestId('progress-inaccessible')).toContainText('1')
  await expect(page.getByTestId('journal-entry-recon-entry')).toContainText('Восстановление')
  await expect(page.getByTestId('journal-entry-search-entry')).toContainText('Поиск')
  await expect(page.getByTestId('journal-entry-system-entry')).toContainText('Системное событие')
  await expect(page.getByTestId('mode-banner').locator('svg')).toHaveCount(1)
})

test('persistence capability states are disclosed without claiming guaranteed backup', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'storage', {
      configurable: true,
      value: {
        persisted: async () => true,
        persist: async () => true,
      },
    })
  })
  const caseValue = caseFixture({ interaction_journal: [journalEntry('engaged', 'search', 'Проверил куртку.')] })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('storage-notice')).toContainText('постоянное хранилище')
  await expect(page.getByTestId('storage-notice')).toContainText('экспорт')
  await expect(page.getByTestId('storage-notice')).toContainText('Облачной резервной копии')
})

test('dark reduced-motion increased-contrast and responsive presentation contracts are present', async ({ page }) => {
  const tokens = readFileSync(resolve(process.cwd(), 'app/assets/css/tokens.css'), 'utf8')
  const appCss = readFileSync(resolve(process.cwd(), 'app/assets/css/app.css'), 'utf8')
  expect(tokens).toContain('@media (prefers-color-scheme: dark)')
  expect(tokens).toContain('@media (prefers-contrast: more)')
  expect(appCss).toContain('@media (prefers-reduced-motion: reduce)')

  await page.emulateMedia({ colorScheme: 'dark', reducedMotion: 'reduce' })
  await page.setViewportSize({ width: 405, height: 820 })
  const caseValue = caseFixture()
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  expect(await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--md-bg').trim())).toBe('#0d1218')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
})

test.describe('assistant guard isolation', () => {
  test.use({ baseURL: 'http://127.0.0.1:3001' })

  test('blocked reconstruction proposal is not carried into a newly loaded search-mode proposal', async ({ page }) => {
    const reconstruction = caseFixture({ current_mode: 'reconstruction', candidates: [] })
    const search = caseFixture({
      current_mode: 'search',
      updated_at: '2026-09-10T07:02:00Z',
      candidates: [candidate('candidate-2', 'сумка')],
    })
    let proposalCalls = 0

    await page.route('**/api/v1/proposal/next', async (route) => {
      proposalCalls += 1
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          case: search,
          proposal: {
            kind: 'next_action',
            candidate_id: 'candidate-2',
            target: 'сумка',
            copy_key: 'search.next_action',
            rationale_codes: ['episode-linked'],
            related_statement_ids: [],
          },
          guard_code: null,
        }),
      })
    })

    await seedCase(page, reconstruction)
    await page.goto(`/cases/${reconstruction.case_id}`)
    await expect(page.getByTestId('reconstruction-panel')).toBeVisible()
    await expect(page.getByTestId('provider-disclosure')).toHaveCount(0)
    expect(proposalCalls).toBe(0)

    await seedCase(page, search)
    await page.goto(`/cases/${search.case_id}`)
    await expect(page.getByTestId('next-action-target')).toHaveText('сумка')
    await expect(page.getByTestId('guard-block')).toHaveCount(0)
    expect(proposalCalls).toBe(1)
  })
})
