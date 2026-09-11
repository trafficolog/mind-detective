import { expect, test } from '@playwright/test'
import { candidate, caseFixture, seedCase } from './helpers'

test('empty planner asks for more information without inventing a location', async ({ page }) => {
  const caseValue = caseFixture({ candidates: [] })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('need-more-information')).toBeVisible()
  await expect(page.getByTestId('next-action-target')).toHaveCount(0)
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
