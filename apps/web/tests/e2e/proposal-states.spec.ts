import { expect, test } from '@playwright/test'
import { candidate, caseFixture, seedCase, storedCase } from './helpers'

test('empty planner asks for more information without inventing a location', async ({ page }) => {
  const caseValue = caseFixture({ candidates: [] })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('need-more-information')).toBeVisible()
  await expect(page.getByTestId('next-action-target')).toHaveCount(0)
  await expect(page.getByTestId('search-target-form')).toBeVisible()
  await expect(page.getByTestId('search-target-input')).toHaveAttribute('placeholder', /место/i)
})

test('structured search target becomes the exact deterministic candidate instead of echoing free prose', async ({ page }) => {
  const caseValue = caseFixture({ candidates: [] })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await page.getByTestId('search-target-input').fill('карман синего рюкзака')
  await page.getByTestId('add-search-target').click()

  await expect(page.getByTestId('next-action-target')).toHaveText('карман синего рюкзака')
  const persisted = await storedCase(page, caseValue.case_id)
  expect(persisted?.candidates).toHaveLength(1)
  expect(persisted?.candidates[0]?.target).toBe('карман синего рюкзака')
  expect(persisted?.statements).toHaveLength(1)
  expect(persisted?.statements[0]?.original_text).toBe('карман синего рюкзака')
})

test('rejected candidate is not immediately proposed again', async ({ page }) => {
  const caseValue = caseFixture({
    candidates: [
      candidate('candidate-1', 'рюкзак'),
      { ...candidate('candidate-2', 'куртка'), route_relation: 'indirect' },
    ],
  })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('next-action-target')).toHaveText('рюкзак')
  await page.getByTestId('reject-action').click()
  await expect(page.getByTestId('action-reject-dialog')).toBeVisible()
  await page.getByTestId('reject-reason').selectOption('irrelevant')
  await page.getByTestId('confirm-reject').click()
  await expect(page.getByTestId('next-action-target')).toHaveText('куртка')

  await expect(page.getByRole('button', { name: /Удалить/ })).toHaveCount(0)
})
