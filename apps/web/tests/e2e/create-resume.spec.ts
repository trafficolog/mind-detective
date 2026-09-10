import { expect, test } from '@playwright/test'

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
  await expect(page.getByTestId('mode-choice')).toBeVisible()

  await page.getByRole('button', { name: 'Перейти к поиску' }).click()
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
