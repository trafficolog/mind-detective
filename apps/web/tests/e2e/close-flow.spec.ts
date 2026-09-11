import { expect, test } from '@playwright/test'
import { caseFixture, seedCase, storedCase } from './helpers'

test('found elsewhere closes case with explicit research context', async ({ page }) => {
  const caseValue = caseFixture()
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await page.getByTestId('found-case').click()
  await expect(page.getByTestId('close-case-dialog')).toBeVisible()
  await page.getByTestId('found-context').selectOption('elsewhere_unplanned')
  await page.getByTestId('close-found').click()

  await expect(page.getByTestId('case-outcome')).toContainText('найдено')
  const stored = await storedCase(page, caseValue.case_id)
  expect(stored?.lifecycle).toBe('closed_found')
  expect(stored?.outcome).toMatchObject({ found_context: 'elsewhere_unplanned' })
})

test('unresolved close is distinct from found', async ({ page }) => {
  const caseValue = caseFixture({ case_id: 'case-unresolved' })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await page.getByTestId('found-case').click()
  await page.getByTestId('close-unresolved').click()

  await expect(page.getByTestId('case-outcome')).toContainText('без результата')
  expect((await storedCase(page, caseValue.case_id))?.lifecycle).toBe('closed_unresolved')
})
