import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'

test('deterministic create and mutations do not require case API network calls', async ({ page }) => {
  let createCalls = 0
  let commandCalls = 0
  await page.route('**/api/v1/case/create', async (route) => {
    createCalls += 1
    await route.abort('failed')
  })
  await page.route('**/api/v1/case/command', async (route) => {
    commandCalls += 1
    await route.abort('failed')
  })

  await page.goto('/')
  await page.getByLabel('Что потерялось?').fill('ключи')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\/([^/]+)$/)
  const caseId = page.url().split('/').at(-1)!

  await expect(page.getByTestId('mode-choice')).toHaveCount(0)
  await expect(page.getByTestId('mode-banner')).toContainText('Физический поиск')

  await page.getByTestId('search-target-input').fill('карман рюкзака')
  await page.getByTestId('add-search-target').click()
  await expect(page.getByTestId('next-action-target')).toHaveText('карман рюкзака')

  await page.getByTestId('mark-checked').click()
  await expect.poll(async () => (await storedCase(page, caseId))?.search_checks.length).toBe(1)

  await page.getByTestId('pause-case').click()
  await expect(page.getByTestId('paused-banner')).toBeVisible()
  await page.getByRole('button', { name: 'Продолжить' }).click()
  await expect(page.getByTestId('paused-banner')).toHaveCount(0)

  expect(createCalls).toBe(0)
  expect(commandCalls).toBe(0)
})
