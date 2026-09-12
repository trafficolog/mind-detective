import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'

test('preloaded PWA continues reconstruction and Search deterministically while offline', async ({ page, context, browserName }) => {
  test.skip(browserName !== 'chromium', 'Task 7 canonical offline proof runs in Chromium')

  let caseApiRequests = 0
  page.on('request', (request) => {
    try {
      if (new URL(request.url()).pathname.startsWith('/api/v1/case/')) caseApiRequests += 1
    } catch {
      // Ignore non-URL browser internals.
    }
  })

  await page.goto('http://127.0.0.1:3002/')
  await page.evaluate(async () => {
    if (!('serviceWorker' in navigator)) throw new Error('MD_WEB_SERVICE_WORKER_UNAVAILABLE')
    await navigator.serviceWorker.ready
  })
  await page.reload()
  await expect.poll(async () => await page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true)
  await expect(page.getByTestId('offline-route-ready')).toBeVisible()

  await page.getByLabel('Что потерялось?').fill('ключи')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\/([^/]+)$/)
  const caseId = page.url().split('/').at(-1)!

  await page.getByTestId('enter-reconstruction').click()
  await expect(page.getByTestId('reconstruction-panel')).toBeVisible()

  const freeAccount = 'Я пришёл домой и помню ключи в руке, но дальше последовательность неясна.'
  await page.getByTestId('free-account-input').fill(freeAccount)
  await page.getByTestId('free-account-submit').click()
  await expect(page.getByTestId('free-account-saved')).toContainText(freeAccount)

  caseApiRequests = 0
  await context.setOffline(true)
  await Promise.all([
    page.waitForEvent('load'),
    page.evaluate(() => window.location.reload()),
  ])

  await expect(page).toHaveURL(new RegExp(`/cases/${caseId}$`))
  await expect(page.getByTestId('reconstruction-panel')).toBeVisible()
  await expect(page.getByTestId('free-account-saved')).toContainText(freeAccount)

  const statementText = 'В 17:20 я помню ключи у себя в руке'
  await page.getByTestId('statement-type').selectOption('recollection')
  await page.getByTestId('statement-text').fill(statementText)
  await page.getByTestId('statement-event-time').fill('2026-09-12T17:20')
  await page.getByTestId('statement-submit').click()
  await expect(page.getByTestId('structured-evidence')).toContainText(statementText)

  await page.getByTestId('timeline-event-label').fill('Последний подтверждённый контакт')
  await page.getByTestId('timeline-event-statement').selectOption({ label: statementText })
  await page.getByTestId('timeline-event-time').fill('2026-09-12T17:20')
  await page.getByTestId('timeline-add-event').click()
  await page.getByTestId('timeline-last-supported').selectOption({ label: statementText })
  await page.getByTestId('timeline-rebuild').click()
  await expect(page.getByTestId('timeline-summary')).toBeVisible()

  await page.getByTestId('switch-to-search').click()
  await expect(page.getByTestId('mode-banner')).toContainText('Физический поиск')
  await page.getByTestId('search-target-input').fill('карманы куртки')
  await page.getByTestId('add-search-target').click()
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')
  await page.getByTestId('mark-checked').click()

  await expect.poll(async () => (await storedCase(page, caseId))?.search_checks.length).toBe(1)
  const persisted = await storedCase(page, caseId)
  expect(persisted?.current_mode).toBe('search')
  expect(persisted?.interaction_journal.some(entry => (
    entry.author === 'user'
    && entry.mode === 'reconstruction'
    && entry.entry_type === 'free_account'
    && entry.text === freeAccount
  ))).toBe(true)
  expect(persisted?.statements.some(statement => statement.original_text === statementText)).toBe(true)
  expect(persisted?.timeline?.events).toHaveLength(1)
  expect(persisted?.search_checks[0]?.result).toBe('not_found')
  expect(caseApiRequests).toBe(0)
})
