import { expect, test } from '@playwright/test'
import { caseFixture, seedCase, storedCase } from './helpers'

test('production creation is one field and preserves a paused case for resume', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByTestId('create-case-form')).toBeVisible()
  await expect(page.getByLabel('Что потерялось?')).toBeVisible()
  await expect(page.getByTestId('start-search')).toBeVisible()
  await expect(page.getByText('Как работать')).toHaveCount(0)
  await expect(page.getByTestId('experimental-arm')).toHaveCount(0)

  await page.getByLabel('Что потерялось?').fill('ключи')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\//)
  await expect(page.getByTestId('mode-choice')).toHaveCount(0)
  await expect(page.getByTestId('mode-banner')).toContainText('Физический поиск')

  await page.getByTestId('pause-case').click()
  await expect(page.getByTestId('paused-banner')).toBeVisible()

  await page.goto('/')
  await expect(page.getByRole('link', { name: /ключи/ })).toBeVisible()
  await page.getByRole('link', { name: /ключи/ }).click()
  await expect(page.getByTestId('paused-banner')).toBeVisible()

  await page.getByRole('button', { name: 'Продолжить' }).click()
  await expect(page.getByTestId('paused-banner')).toHaveCount(0)
  await expect(page.getByTestId('mode-banner')).toContainText('Физический поиск')
})

test('legacy reconstruction case opens the state-first panel and preserves explicit handoff to physical search', async ({ page }) => {
  const legacy = caseFixture({
    case_id: 'case-reconstruction-boundary',
    current_mode: 'reconstruction',
    candidates: [],
  })
  await seedCase(page, legacy)
  await page.goto(`/cases/${legacy.case_id}`)

  await expect(page.getByTestId('reconstruction-panel')).toBeVisible()
  await expect(page.getByTestId('interaction-dock').getByRole('button', { name: 'Написать' })).toHaveCount(0)
  await expect(page.getByTestId('next-action-card')).toHaveCount(0)

  await page.getByTestId('switch-to-search').click()
  await expect(page.getByTestId('mode-banner')).toContainText('Физический поиск')
  await expect.poll(async () => (await storedCase(page, legacy.case_id))?.current_mode).toBe('search')
})
