import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'
import { addZone, createMobileCase, onboarded } from './mobileHelpers'

test.use({ viewport: { width: 430, height: 844 } })

test('M9 photo or file case uses sources, digital methods and «Файл найден»', async ({ page }) => {
  await onboarded(page)
  await page.goto('/new')
  await page.getByRole('radio', { name: 'Фото или файл' }).click()
  await expect(page.locator('#new-case-title')).toHaveAttribute('placeholder', 'Например, фото с дня рождения')
  const caseId = await createMobileCase(page, 'Фото с дня рождения', 'digital', 'search')
  expect((await storedCase(page, caseId))?.constraints).toEqual(['item_kind:digital'])

  await expect(page.getByText('Источники проверки')).toBeVisible()
  await addZone(page, 'Телефон → Фото → Недавно удалённые')
  await addZone(page, 'Мессенджер → чат с семьёй')
  await expect(page.getByTestId('search-progress')).toContainText('Следующий источник')

  await page.getByTestId('check-now').click()
  await expect(page.getByRole('dialog')).toContainText('Проверка источника')
  await expect(page.getByRole('radio', { name: 'С фонарём' })).toHaveCount(0)
  await page.getByRole('radio', { name: 'Проверил «Удалённые» / корзину' }).click()
  await page.getByTestId('check-submit').click()
  await expect(page.getByTestId('search-check-card')).toContainText('«Удалённые» / корзина')
  expect((await storedCase(page, caseId))?.search_checks[0]?.method).toBe('trash')

  await page.locator('[data-nav="search"]').click()
  await page.getByTestId('finish-unresolved').click()
  await expect(page.getByRole('radio', { name: 'Файл найден' })).toBeVisible()
  await page.getByRole('radio', { name: 'Файл найден' }).click()
  await expect(page.getByRole('radio', { name: 'В другом, незапланированном источнике' })).toBeVisible()
  await page.getByRole('radio', { name: 'В другом, незапланированном источнике' }).click()
  await page.getByTestId('close-submit').click()
  await expect(page.getByTestId('case-outcome')).toContainText('Фото с дня рождения — найдено')
  const stored = await storedCase(page, caseId)
  expect(stored?.lifecycle).toBe('closed_found')
  expect(stored?.outcome).toEqual({ found_context: 'elsewhere_unplanned' })
})
