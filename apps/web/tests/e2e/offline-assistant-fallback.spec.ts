import { expect, test } from '@playwright/test'
import { candidate, caseFixture, seedCase } from './helpers'

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
