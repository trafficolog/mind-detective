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

test('high-risk forgotten action exits lost-item creation before a Case is persisted', async ({ page }) => {
  await page.goto('/')
  await page.getByTestId('item-label').fill('Принимал ли я уже таблетки?')
  await page.getByTestId('start-search').click()

  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByTestId('safety-route')).toContainText('не использует поиск вещей')
  await expect(page.getByTestId('safety-route')).toContainText('MD_SAFE_MEDICATION_ACTION')
  await expect(page.getByTestId('case-list').getByText('Принимал ли я уже таблетки?')).toHaveCount(0)
})

test.describe('English locale contract', () => {
  test.use({ locale: 'en-US' })

  test('browser locale drives visible checklist copy', async ({ page }) => {
    const caseValue = caseFixture({ case_id: 'case-en-locale', current_mode: 'search' })
    await seedCase(page, caseValue)
    await page.goto(`/cases/${caseValue.case_id}`)

    await expect(page.getByTestId('mode-banner')).toContainText('Physical search')
    await expect(page.getByRole('button', { name: 'Write' })).toBeVisible()
  })
})

test('assistant arm has an explicit model-provider processing disclosure contract', () => {
  const source = readFileSync(resolve(process.cwd(), 'app/pages/cases/[id].vue'), 'utf8')
  expect(source).toContain('data-testid="provider-disclosure"')
  expect(source).toContain("privacy.assistant_provider")
  expect(source).toMatch(/arm\s*===\s*['\"]assistant['\"]/)
})
