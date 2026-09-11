import { expect, test } from '@playwright/test'
import { candidate, caseFixture, searchCheck, seedCase, storedCase } from './helpers'

test('one-tap not-found check commits canonical progress locally without command network', async ({ page }) => {
  const caseValue = caseFixture()
  let commandCalls = 0
  await page.route('**/api/v1/case/command', async (route) => {
    commandCalls += 1
    await route.abort('failed')
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')
  await expect(page.getByTestId('progress-checked')).toContainText('0')
  await expect(page.getByTestId('progress-remaining')).toContainText('1')
  await expect(page.getByTestId('mark-checked')).toHaveText('Проверил — не нашёл')

  await page.getByTestId('mark-checked').click()
  await expect(page.getByTestId('progress-checked')).toContainText('1')
  await expect(page.getByTestId('progress-remaining')).toContainText('0')
  const persisted = await storedCase(page, caseValue.case_id)
  expect(persisted?.search_checks).toHaveLength(1)
  expect(persisted?.search_checks[0]?.method).toBe('reported_check')
  expect(persisted?.search_checks[0]?.result).toBe('not_found')
  expect(commandCalls).toBe(0)
  await expect(page.getByTestId('check-quality-dialog')).toHaveCount(0)
})

test('quality clarification appears only when a reported check is decision-relevant again', async ({ page }) => {
  const prior = searchCheck('check-1', 'candidate-1', 'карманы куртки', 'reported_check')
  const caseValue = caseFixture({
    updated_at: '2026-09-10T07:01:10Z',
    candidates: [candidate('candidate-1', 'карманы куртки', 'partial')],
    search_checks: [prior],
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')
  await expect(page.getByTestId('check-quality-dialog')).toBeVisible()
  await expect(page.getByTestId('check-quality-dialog')).toContainText('карманы куртки')
})
