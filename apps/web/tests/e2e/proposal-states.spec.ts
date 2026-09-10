import { expect, test } from '@playwright/test'
import { candidate, caseFixture, seedCase } from './helpers'

test('empty planner asks for more information without inventing a location', async ({ page }) => {
  const caseValue = caseFixture({ candidates: [] })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('need-more-information')).toBeVisible()
  await expect(page.getByTestId('next-action-target')).toHaveCount(0)
})

test('guard block shows reviewed fallback and never exposes rejected raw proposal text', async ({ page }) => {
  const caseValue = caseFixture({ current_mode: 'reconstruction', candidates: [] })
  await page.route('**/api/v1/proposal/next', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        case: {
          ...caseValue,
          updated_at: '2026-09-10T07:01:00Z',
          interaction_journal: [{
            id: 'guard-e2e',
            author: 'system',
            mode: 'system',
            entry_type: 'guard_block',
            text: 'guard.ai_proposal_blocked',
            created_at: '2026-09-10T07:01:00Z',
            statement_ids: [],
            search_check_ids: [],
          }],
        },
        proposal: {
          kind: 'clarification',
          candidate_id: null,
          target: null,
          copy_key: 'reconstruction.clarification',
          rationale_codes: [],
          related_statement_ids: [],
        },
        guard_code: 'MD_G_RECON_NEW_LOCATION',
      }),
    })
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('guard-block')).toBeVisible()
  await expect(page.getByTestId('guard-block')).toContainText('не прошло проверку безопасности')
  await expect(page.getByText('секретная машина')).toHaveCount(0)
  await expect(page.getByTestId('journal-entry-guard-e2e')).toContainText('Безопасность')
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
