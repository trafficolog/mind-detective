import { expect, test } from '@playwright/test'
import { caseFixture, journalEntry, seedCase, storedCase } from './helpers'

const legacyV1 = {
  schema: 'mind-detective-case/v1',
  case_id: 'legacy-import',
  item_label: 'паспорт',
  created_at: '2026-09-09T18:00:00Z',
  updated_at: '2026-09-09T18:05:00Z',
  lifecycle: 'active',
  statements: [],
  timeline: null,
  search_checks: [],
  candidates: [],
  next_action: null,
  constraints: [],
  outcome: null,
}

test('valid v1 import migrates locally with case validation network unavailable and future schema is rejected', async ({ page }) => {
  let validationRequests = 0
  await page.route('**/api/v1/case/validate', async (route) => {
    validationRequests += 1
    await route.abort('failed')
  })

  await page.goto('/')
  await expect(page.getByTestId('offline-route-ready')).toBeVisible()
  await page.getByTestId('case-import').setInputFiles({
    name: 'legacy.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(legacyV1)),
  })

  await expect(page).toHaveURL(/\/cases\/legacy-import/)
  const migrated = await storedCase(page, 'legacy-import')
  expect(migrated?.schema).toBe('mind-detective-case/v2')
  expect(migrated?.current_mode).toBe('unselected')
  expect(migrated?.interaction_journal).toEqual([])
  expect(migrated?.action_feedback).toEqual([])
  expect(validationRequests).toBe(0)

  await page.goto('/')
  await expect(page.getByTestId('case-import')).toBeVisible()
  await page.getByTestId('case-import').setInputFiles({
    name: 'future.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ schema: 'mind-detective-case/v999' })),
  })
  await expect(page.getByRole('status')).toContainText('не поддерживается')
  expect(validationRequests).toBe(0)
})

test('engaged case exposes durability warning install education and explicit JSON export', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'storage', {
      configurable: true,
      value: {
        persisted: async () => false,
        persist: async () => false,
      },
    })
  })
  const caseValue = caseFixture({
    interaction_journal: [journalEntry('search-1', 'search', 'Проверил куртку.')],
  })
  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await expect(page.getByTestId('storage-notice')).toBeVisible()
  await expect(page.getByTestId('storage-notice')).toContainText('не гарантирует')
  await expect(page.getByTestId('install-education')).toBeVisible()
  await expect(page.getByTestId('case-data-actions')).toBeVisible()

  const downloadPromise = page.waitForEvent('download')
  await page.getByTestId('export-case').click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toContain(caseValue.case_id)
})

test('reconstruction Case v2 survives IndexedDB reload without dropping canonical reconstruction fields', async ({ page }) => {
  const freeAccount = 'Я пришёл домой, положил ключи и позже заметил, что их нет.'
  const caseValue = caseFixture({
    case_id: 'reconstruction-storage',
    current_mode: 'reconstruction',
    interaction_journal: [
      {
        id: 'free-1',
        author: 'user',
        mode: 'reconstruction',
        entry_type: 'free_account',
        text: freeAccount,
        created_at: '2026-09-12T17:25:00+03:00',
        statement_ids: [],
        search_check_ids: [],
      },
    ],
    statements: [
      {
        id: 'stmt-1',
        source: 'user',
        statement_type: 'recollection',
        original_text: 'В 17:20 ключи были у меня в руке',
        recorded_at: '2026-09-12T17:26:00+03:00',
        event_time: '2026-09-12T17:20:00+03:00',
        user_confirmation: true,
        supporting_evidence_ids: [],
        limitations: [],
      },
    ],
    timeline: {
      last_supported_interaction_id: 'stmt-1',
      first_noticed_missing_id: null,
      events: [
        {
          id: 'event-1',
          label: 'Последний подтверждённый контакт',
          statement_ids: ['stmt-1'],
          event_time: '2026-09-12T17:20:00+03:00',
          time_precision: 'approximate',
        },
      ],
      unknown_intervals: ['После 17:20 точное время неизвестно'],
      contradictions: ['MD_TIME_REFERENCE_MISSING'],
    },
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)
  await expect(page.getByTestId('reconstruction-panel')).toBeVisible()
  await expect(page.getByTestId('free-account-saved')).toContainText(freeAccount)
  await expect(page.getByTestId('timeline-summary')).toBeVisible()

  await page.reload()
  await expect(page.getByTestId('reconstruction-panel')).toBeVisible()
  await expect(page.getByTestId('free-account-saved')).toContainText(freeAccount)

  const persisted = await storedCase(page, caseValue.case_id)
  expect(persisted?.current_mode).toBe('reconstruction')
  expect(persisted?.interaction_journal).toEqual(caseValue.interaction_journal)
  expect(persisted?.statements).toEqual(caseValue.statements)
  expect(persisted?.timeline).toEqual(caseValue.timeline)
})
