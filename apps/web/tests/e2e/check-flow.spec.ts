import { expect, test } from '@playwright/test'
import { candidate, caseFixture, searchCheck, seedCase, storedCase } from './helpers'

test('one-tap check stays pending without optimistic canonical progress', async ({ page }) => {
  const caseValue = caseFixture()
  let releaseCommand!: () => void
  const gate = new Promise<void>(resolve => { releaseCommand = resolve })

  await page.route('**/api/v1/case/command', async (route) => {
    const body = route.request().postDataJSON() as { command?: { command_type?: string } }
    if (body.command?.command_type === 'record_search_check') {
      await gate
    }
    await route.continue()
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')
  await expect(page.getByTestId('progress-checked')).toContainText('0')
  await expect(page.getByTestId('progress-remaining')).toContainText('1')

  await page.getByTestId('mark-checked').click()
  await expect(page.getByTestId('next-action-card')).toHaveAttribute('aria-busy', 'true')
  await expect(page.getByTestId('progress-checked')).toContainText('0')
  await expect(page.getByTestId('progress-remaining')).toContainText('1')
  expect((await storedCase(page, caseValue.case_id))?.search_checks).toHaveLength(0)

  releaseCommand()
  await expect(page.getByTestId('next-action-card')).toHaveAttribute('aria-busy', 'false')
  await expect(page.getByTestId('progress-checked')).toContainText('1')
  await expect(page.getByTestId('progress-remaining')).toContainText('0')
  expect((await storedCase(page, caseValue.case_id))?.search_checks[0]?.method).toBe('reported_check')
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
