import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'

test('preloaded PWA completes the canonical search workflow with the browser offline', async ({ page, context, browserName }) => {
  let apiRequests = 0
  page.on('request', (request) => {
    try {
      if (new URL(request.url()).pathname.startsWith('/api/')) apiRequests += 1
    } catch {
      // Ignore non-URL browser internals.
    }
  })

  await page.goto('/')
  await page.evaluate(async () => {
    if (!('serviceWorker' in navigator)) throw new Error('MD_WEB_SERVICE_WORKER_UNAVAILABLE')
    await navigator.serviceWorker.ready
  })
  await page.reload()
  await expect.poll(async () => await page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true)
  await expect(page.getByTestId('offline-route-ready')).toBeVisible()

  apiRequests = 0
  await context.setOffline(true)

  await page.getByLabel('Что потерялось?').fill('ключи')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\/([^/]+)$/)
  const caseId = page.url().split('/').at(-1)!

  await page.getByRole('button', { name: 'Перейти к поиску' }).click()
  await expect(page.getByTestId('mode-banner')).toContainText('Физический поиск')

  await page.getByTestId('search-target-input').fill('карман рюкзака')
  await page.getByTestId('add-search-target').click()
  await expect(page.getByTestId('next-action-target')).toHaveText('карман рюкзака')

  await page.getByTestId('mark-checked').click()
  await expect.poll(async () => (await storedCase(page, caseId))?.search_checks.length).toBe(1)
  await expect(page.getByTestId('check-quality-dialog')).toHaveCount(0)

  await page.getByTestId('search-target-input').fill('полка у двери')
  await page.getByTestId('add-search-target').click()
  await expect(page.getByTestId('next-action-target')).toHaveText('полка у двери')

  await page.getByTestId('reject-action').click()
  await page.getByTestId('reject-reason').selectOption('irrelevant')
  await page.getByTestId('confirm-reject').click()
  await expect(page.getByTestId('next-action-target')).toHaveText('карман рюкзака')
  await expect(page.getByTestId('check-quality-dialog')).toBeVisible()

  await page.getByTestId('check-method').selectOption('visual_systematic')
  await page.getByTestId('save-check-quality').click()
  await expect(page.getByTestId('check-quality-dialog')).toHaveCount(0)
  await expect.poll(async () => (await storedCase(page, caseId))?.search_checks[0]?.method).toBe('visual_systematic')

  await page.getByTestId('pause-case').click()
  await expect(page.getByTestId('paused-banner')).toBeVisible()
  await page.getByRole('button', { name: 'Продолжить' }).click()
  await expect(page.getByTestId('paused-banner')).toHaveCount(0)

  await page.getByTestId('found-case').click()
  await page.getByTestId('found-context').selectOption('current_suggested_action')
  await page.getByTestId('close-found').click()
  await expect(page.getByTestId('case-outcome')).toContainText('найдено')

  const downloadPromise = page.waitForEvent('download')
  await page.getByTestId('export-case').click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toContain(caseId)

  expect(await page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true)
  if (browserName === 'chromium') {
    await Promise.all([
      page.waitForEvent('load'),
      page.evaluate(() => window.location.reload()),
    ])
    await expect(page.getByTestId('case-outcome')).toContainText('найдено')
  }
  expect((await storedCase(page, caseId))?.lifecycle).toBe('closed_found')
  expect(apiRequests).toBe(0)
})
