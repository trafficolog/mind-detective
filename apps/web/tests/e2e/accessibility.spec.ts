import { expect, test } from '@playwright/test'
import { caseFixture, seedCase } from './helpers'

test('active case does not steal keyboard focus and fits narrow mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 720 })
  const caseValue = caseFixture()
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('case-shell')).toBeVisible()
  expect(await page.evaluate(() => document.activeElement?.tagName)).toBe('BODY')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)

  const interactive = page.locator('button:visible, a.primary-action:visible, a.secondary-action:visible')
  const count = await interactive.count()
  for (let index = 0; index < count; index += 1) {
    const box = await interactive.nth(index).boundingBox()
    if (box) expect(box.height).toBeGreaterThanOrEqual(44)
  }
})

test('modal traps focus closes on Escape and restores trigger focus', async ({ page }) => {
  const caseValue = caseFixture()
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  const trigger = page.getByTestId('reject-action')
  await trigger.focus()
  await trigger.click()
  const dialog = page.getByTestId('action-reject-dialog')
  await expect(dialog).toBeVisible()

  expect(await page.evaluate(() => Boolean(document.activeElement?.closest('[role="dialog"]')))).toBe(true)
  await page.keyboard.press('Tab')
  expect(await page.evaluate(() => Boolean(document.activeElement?.closest('[role="dialog"]')))).toBe(true)
  await page.keyboard.press('Escape')

  await expect(dialog).toHaveCount(0)
  await expect(trigger).toBeFocused()
})
