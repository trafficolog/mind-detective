import { expect, test } from '@playwright/test'
import { candidate, caseFixture, seedCase } from './helpers'

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

test.describe('English assistant locale contract', () => {
  test.use({ locale: 'en-US' })

  test('proposal request uses the browser locale', async ({ page }) => {
    const caseValue = caseFixture({ case_id: 'case-en-assistant', current_mode: 'search' })
    let requestLocale: string | null = null
    await page.route('**/api/v1/proposal/next', async (route) => {
      const body = route.request().postDataJSON() as { locale?: string }
      requestLocale = body.locale ?? null
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          case: caseValue,
          proposal: {
            kind: 'need_more_information',
            candidate_id: null,
            target: null,
            copy_key: 'empty.add_supported_place_or_reconstruct',
            rationale_codes: [],
            related_statement_ids: [],
          },
          guard_code: null,
        }),
      })
    })

    await seedCase(page, caseValue)
    await page.goto(`/cases/${caseValue.case_id}`)
    await expect.poll(() => requestLocale).toBe('en')
  })
})

test('blocked reconstruction proposal is not carried into a newly loaded search-mode proposal', async ({ page }) => {
  const reconstruction = caseFixture({ current_mode: 'reconstruction', candidates: [] })
  const search = caseFixture({
    current_mode: 'search',
    updated_at: '2026-09-10T07:02:00Z',
    candidates: [candidate('candidate-2', 'сумка')],
  })
  let proposalCalls = 0

  await page.route('**/api/v1/proposal/next', async (route) => {
    proposalCalls += 1
    if (proposalCalls === 1) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          case: {
            ...reconstruction,
            interaction_journal: [{
              id: 'guard-scenario',
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
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        case: search,
        proposal: {
          kind: 'next_action',
          candidate_id: 'candidate-2',
          target: 'сумка',
          copy_key: 'search.next_action',
          rationale_codes: ['episode-linked'],
          related_statement_ids: [],
        },
        guard_code: null,
      }),
    })
  })

  await seedCase(page, reconstruction)
  await page.goto(`/cases/${reconstruction.case_id}`)
  await expect(page.getByTestId('guard-block')).toBeVisible()
  await expect(page.getByText('секретная машина')).toHaveCount(0)

  await seedCase(page, search)
  await page.goto(`/cases/${search.case_id}`)
  await expect(page.getByTestId('next-action-target')).toHaveText('сумка')
  await expect(page.getByTestId('guard-block')).toHaveCount(0)
  await expect(page.getByText('секретная машина')).toHaveCount(0)
})
