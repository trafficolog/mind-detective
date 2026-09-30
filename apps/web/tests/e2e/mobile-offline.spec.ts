import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'

test.use({ viewport: { width: 430, height: 844 } })

test('preloaded mobile PWA runs reconstruction and search while offline', async ({ page, context }) => {
  await page.addInitScript(() => window.localStorage.setItem('md.mobile.onboarded', '1'))
  await page.goto('/')
  await page.evaluate(async () => { await navigator.serviceWorker.ready })
  await page.reload()
  await expect.poll(async () => await page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true)
  await expect(page.getByTestId('screen-home')).toBeVisible()

  await context.setOffline(true)
  await page.getByTestId('home-write').click()
  await page.locator('#new-case-title').fill('Ключи')
  await page.getByTestId('create-reconstruction').click()
  await expect(page).toHaveURL(/\/cases\//)
  const caseId = new URL(page.url()).pathname.split('/').at(-1)!
  await page.locator('#free-account').fill('Рассказ офлайн')
  await page.getByTestId('free-account-save').click()
  await page.getByTestId('go-search').click()
  await page.getByTestId('add-zone').click()
  await page.locator('#zone-name').fill('Прихожая')
  await page.getByTestId('zone-submit').click()
  await page.getByTestId('check-now').click()
  await page.getByTestId('check-submit').click()
  await expect(page.getByTestId('search-check-card')).toHaveCount(1)
  const stored = await storedCase(page, caseId)
  expect(stored?.search_checks).toHaveLength(1)
  expect(stored?.current_mode).toBe('search')
  await context.setOffline(false)
})
