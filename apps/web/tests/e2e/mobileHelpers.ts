import { expect, type Page } from '@playwright/test'

/** Skips splash/onboarding (M1 covers it) and optionally configures an n8n server. */
export async function onboarded(page: Page, extra: Record<string, string> = {}): Promise<void> {
  await page.addInitScript((values) => {
    window.localStorage.setItem('md.mobile.onboarded', '1')
    for (const [key, value] of Object.entries(values)) window.localStorage.setItem(key, value)
  }, extra)
}

export async function createMobileCase(page: Page, title: string, kind: 'physical' | 'digital', start: 'reconstruction' | 'search'): Promise<string> {
  await page.goto('/new')
  if (kind === 'digital') await page.getByRole('radio', { name: 'Фото или файл' }).click()
  await page.locator('#new-case-title').fill(title)
  await page.getByTestId(start === 'reconstruction' ? 'create-reconstruction' : 'create-search').click()
  await expect(page).toHaveURL(/\/cases\/[^/?]+\?tab=/)
  return new URL(page.url()).pathname.split('/').at(-1)!
}

export async function addEvent(page: Page, title: string, precision: 'Точное' | 'Примерное' | 'Неизвестное', digits = ''): Promise<void> {
  await page.getByTestId('add-event').click()
  await page.locator('#event-title').fill(title)
  await page.getByRole('radio', { name: precision }).click()
  if (digits) await page.getByTestId('event-time').pressSequentially(digits)
  await page.getByTestId('event-submit').click()
  await expect(page.getByTestId('sheet-event')).toHaveCount(0)
}

export async function addZone(page: Page, name: string): Promise<void> {
  await page.getByTestId('add-zone').click()
  await page.locator('#zone-name').fill(name)
  await page.getByTestId('zone-submit').click()
  await expect(page.getByTestId('sheet-zone')).toHaveCount(0)
}
