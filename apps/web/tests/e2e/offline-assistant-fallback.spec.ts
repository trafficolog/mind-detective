import { expect, test } from '@playwright/test'
import { candidate, caseFixture, seedCase, storedCase } from './helpers'

test('assistant transport failure falls back locally without reconnect replay', async ({ page }) => {
  const caseValue = caseFixture({
    candidates: [candidate('candidate-1', 'карманы куртки')],
  })
  let proposalCalls = 0

  await page.route('**/api/v1/proposal/next', async (route) => {
    proposalCalls += 1
    await route.abort('failed')
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('provider-disclosure')).toBeVisible()
  await expect(page.getByTestId('assistant-offline-fallback')).toBeVisible()
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')

  const callsBeforeReconnect = proposalCalls
  await page.evaluate(() => window.dispatchEvent(new Event('online')))
  await page.waitForTimeout(100)

  expect(proposalCalls).toBe(callsBeforeReconnect)
  await expect(page.getByTestId('assistant-offline-fallback')).toBeVisible()
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')
})

test('execution contract skew is surfaced while local deterministic mutation remains committed', async ({ page }) => {
  const caseValue = caseFixture({
    case_id: 'case-skew-e2e',
    current_mode: 'unselected',
    candidates: [],
  })

  await page.route('**/api/v1/proposal/next', async (route) => {
    await route.fulfill({
      status: 409,
      contentType: 'application/json',
      body: JSON.stringify({
        code: 'MD_WEB_EXECUTION_CONTRACT_MISMATCH',
        message: 'client execution contract does not match server execution contract',
      }),
    })
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)
  await page.getByTestId('mode-choice').getByRole('button', { name: 'Перейти к поиску' }).click()

  await expect(page.getByTestId('execution-contract-mismatch')).toBeVisible()
  await expect(page.getByTestId('command-error')).toHaveCount(0)
  await expect(page.getByTestId('mode-choice')).toHaveCount(0)

  const persisted = await storedCase(page, caseValue.case_id)
  expect(persisted?.current_mode).toBe('search')
})
