import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { expect, test } from '@playwright/test'
import { caseFixture, seedCase, storedCase } from './helpers'

test('closed case keeps export and confirmed selective delete controls', async ({ page }) => {
  const caseValue = caseFixture({
    case_id: 'case-post-close',
    lifecycle: 'closed_found',
    outcome: { found_context: 'unknown' },
  })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('case-outcome')).toBeVisible()
  await expect(page.getByTestId('export-case')).toBeVisible()
  await page.getByTestId('delete-case').click()
  await expect(page.getByTestId('delete-case-confirmation')).toBeVisible()
  await page.getByTestId('confirm-delete-case').click()
  await expect.poll(async () => await storedCase(page, caseValue.case_id)).toBeNull()
})

test('browser locale drives visible copy and proposal request locale', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'language', { configurable: true, value: 'en-US' })
  })
  const caseValue = caseFixture({ case_id: 'case-en-locale', current_mode: 'search' })
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

  await expect(page.getByTestId('mode-banner')).toContainText('Physical search')
  await expect(page.getByRole('button', { name: 'Write' })).toBeVisible()
  await expect.poll(() => requestLocale).toBe('en')
})

test('assistant arm has an explicit model-provider processing disclosure contract', () => {
  const source = readFileSync(resolve(process.cwd(), 'app/pages/cases/[id].vue'), 'utf8')
  expect(source).toContain('data-testid="provider-disclosure"')
  expect(source).toContain("privacy.assistant_provider")
  expect(source).toMatch(/arm\s*===\s*['\"]assistant['\"]/)
})
