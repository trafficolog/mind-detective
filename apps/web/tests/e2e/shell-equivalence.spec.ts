import { expect, test } from '@playwright/test'
import { caseFixture, journalEntry, seedCase } from './helpers'

test('experimental arms expose the same product shell and do not reveal arm identity', async ({ page }) => {
  const caseValue = caseFixture({
    interaction_journal: [
      journalEntry('recon-1', 'reconstruction', 'Я вернулся домой около семи.'),
      journalEntry('search-1', 'search', 'Проверил верхнюю одежду.'),
    ],
  })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  const landmarks = [
    'case-shell',
    'mode-banner',
    'progress-strip',
    'next-action-card',
    'interaction-journal',
    'interaction-dock',
  ]
  for (const landmark of landmarks) {
    await expect(page.getByTestId(landmark)).toBeVisible()
  }

  await expect(page.getByTestId('experimental-arm')).toHaveCount(0)
  await expect(page.getByText('AI-предложение')).toHaveCount(0)
  await expect(page.getByText('Контрольный список')).toHaveCount(0)

  await expect(page.getByTestId('journal-entry-recon-1')).toContainText('Восстановление')
  await expect(page.getByTestId('journal-entry-search-1')).toContainText('Поиск')
})
