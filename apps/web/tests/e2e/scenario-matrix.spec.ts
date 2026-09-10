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
