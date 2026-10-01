import { expect, type Page, test } from '@playwright/test'
import { addZone, createMobileCase, onboarded } from './mobileHelpers'

test.use({ viewport: { width: 320, height: 720 } })

async function checkScreen(page: Page, label: string, screen: string): Promise<void> {
  await expect(page.getByTestId(screen)).toBeVisible()
  await page.waitForLoadState('networkidle')
  // One synchronous DOM snapshot: no per-element waits that could race a re-render.
  const report = await page.evaluate(() => {
    const visible = (el: Element) => {
      const r = el.getBoundingClientRect()
      const style = getComputedStyle(el)
      return r.width > 0 && r.height > 0 && style.visibility !== 'hidden' && style.display !== 'none'
    }
    const offenders: string[] = []
    for (const el of document.querySelectorAll('button, [role="link"], input:not([type="file"]), textarea')) {
      if (!visible(el)) continue
      const r = el.getBoundingClientRect()
      const labelled = el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('placeholder')
      const byLabel = el.id ? document.querySelector(`label[for="${el.id}"]`)?.textContent : null
      const name = (labelled || byLabel || el.closest('label')?.textContent || el.textContent || '').trim()
      if (r.height < 44) offenders.push(`small:${el.outerHTML.slice(0, 80)}`)
      if (!name) offenders.push(`unnamed:${el.outerHTML.slice(0, 80)}`)
    }
    return { overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth, offenders }
  })
  expect(report.overflow, `${label}: no horizontal scroll`).toBe(false)
  expect(report.offenders, `${label}: 44px targets with accessible names`).toEqual([])
}

test('mobile screens fit 320px, keep 44px targets and name every control', async ({ page }) => {
  await page.goto('/')
  await checkScreen(page, 'splash', 'screen-splash')
  await page.getByTestId('splash-start').click()
  await checkScreen(page, 'onboarding', 'screen-onboarding')
  await page.getByTestId('onboarding-finish').click()
  await checkScreen(page, 'home', 'screen-home')
  await page.getByTestId('home-write').click()
  await checkScreen(page, 'new', 'screen-new')
  await page.locator('#new-case-title').fill('Ключи от машины')
  await page.getByTestId('create-reconstruction').click()
  await expect(page.getByTestId('screen-case')).toBeVisible()
  await checkScreen(page, 'reconstruction', 'screen-case')
  await page.locator('#free-account').fill('Рассказ')
  await page.getByTestId('free-account-save').click()
  await page.getByTestId('go-search').click()
  await addZone(page, 'Очень длинное название места для проверки переносов на узком экране телефона')
  await checkScreen(page, 'search', 'screen-case')
  await page.locator('[data-nav="journal"]').click()
  await checkScreen(page, 'journal', 'screen-case')
  await page.locator('[data-nav="cases"]').click()
  await checkScreen(page, 'cases', 'screen-cases')
  await page.goto('/settings')
  await checkScreen(page, 'settings', 'screen-settings')
})

test('bottom sheet takes focus, closes on Escape and returns focus to its trigger', async ({ page }) => {
  await onboarded(page)
  await createMobileCase(page, 'Очки', 'physical', 'search')
  const trigger = page.getByTestId('add-zone')
  await trigger.focus()
  await page.keyboard.press('Enter')
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog).toHaveAttribute('aria-modal', 'true')
  expect(await page.evaluate(() => document.activeElement?.closest('[role="dialog"]') !== null)).toBe(true)
  await page.keyboard.press('Escape')
  await expect(dialog).toHaveCount(0)
  await expect(trigger).toBeFocused()
})

test('case cards and bottom navigation work from the keyboard', async ({ page }) => {
  await onboarded(page)
  await createMobileCase(page, 'Зонт', 'physical', 'reconstruction')
  await page.goto('/cases')
  await page.getByTestId('case-card').focus()
  await page.keyboard.press('Enter')
  await expect(page.getByTestId('screen-case')).toBeVisible()
  await page.locator('[data-nav="journal"]').focus()
  await page.keyboard.press('Enter')
  await expect(page.locator('[data-nav="journal"]')).toHaveAttribute('aria-current', 'page')
})
