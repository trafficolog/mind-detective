import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'

test('state-first reconstruction preserves evidence and transitions explicitly to Search', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Что потерялось?').fill('ключи')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\//)

  const caseId = page.url().split('/cases/')[1]?.split(/[?#]/)[0]
  expect(caseId).toBeTruthy()

  await page.getByTestId('enter-reconstruction').click()
  await expect(page.getByTestId('reconstruction-panel')).toBeVisible()
  await expect(page.getByTestId('mode-banner')).toContainText('Восстановление')

  await expect(page.getByTestId('free-account-card')).toBeVisible()
  await expect(page.getByTestId('statement-capture')).toHaveCount(0)
  await expect(page.getByTestId('timeline-editor')).toHaveCount(0)

  const freeAccount = 'Я пришёл домой, снял куртку и позже заметил, что ключей нет.'
  await page.getByTestId('free-account-input').fill(freeAccount)
  await page.getByTestId('free-account-submit').click()

  await expect(page.getByTestId('free-account-saved')).toContainText(freeAccount)
  await expect(page.getByTestId('statement-capture')).toBeVisible()
  await expect(page.getByTestId('structured-evidence')).not.toContainText(freeAccount)
  await expect(page.getByText('карман рюкзака', { exact: false })).toHaveCount(0)

  await page.getByTestId('statement-type').selectOption('recollection')
  await page.getByTestId('statement-text').fill('В 17:20 я помню ключи у себя в руке')
  await page.getByTestId('statement-event-time').fill('2026-09-12T17:20')
  await page.getByTestId('statement-submit').click()

  await page.getByTestId('statement-type').selectOption('observation')
  await page.getByTestId('statement-text').fill('В 17:15 я заметил, что ключей уже нет')
  await page.getByTestId('statement-event-time').fill('2026-09-12T17:15')
  await page.getByTestId('statement-submit').click()

  await page.getByTestId('statement-type').selectOption('observation')
  await page.getByTestId('statement-text').fill('Позже я снова проверил карманы куртки')
  await page.getByTestId('statement-unknown-time').check()
  await page.getByTestId('statement-limitation').fill('точное время неизвестно')
  await page.getByTestId('statement-submit').click()

  const evidence = page.getByTestId('structured-evidence')
  await expect(evidence).toContainText('В 17:20 я помню ключи у себя в руке')
  await expect(evidence).toContainText('В 17:15 я заметил, что ключей уже нет')
  await expect(evidence).toContainText('точное время неизвестно')

  await page.getByTestId('timeline-event-label').fill('Последний подтверждённый контакт')
  await page.getByTestId('timeline-event-statement').selectOption({ label: 'В 17:20 я помню ключи у себя в руке' })
  await page.getByTestId('timeline-event-time').fill('2026-09-12T17:20')
  await page.getByTestId('timeline-add-event').click()

  await page.getByTestId('timeline-last-supported').selectOption({ label: 'В 17:20 я помню ключи у себя в руке' })
  await page.getByTestId('timeline-first-missing').selectOption({ label: 'В 17:15 я заметил, что ключей уже нет' })
  await page.getByTestId('timeline-rebuild').click()

  await expect(page.getByTestId('timeline-summary')).toBeVisible()
  await expect(page.getByTestId('timeline-unknowns')).toContainText('точное время неизвестно')
  await expect(page.getByTestId('timeline-contradictions')).toContainText('MD_TIME_ORDER_CONTRADICTION')

  await page.getByTestId('switch-to-search').click()
  await expect(page.getByTestId('mode-banner')).toContainText('Физический поиск')
  await expect(page.getByTestId('search-target-form')).toBeVisible()
  await expect(page.getByTestId('reconstruction-panel')).toHaveCount(0)

  const persisted = await storedCase(page, caseId!)
  expect(persisted?.current_mode).toBe('search')
  expect(persisted?.interaction_journal.some(entry => (
    entry.author === 'user'
    && entry.mode === 'reconstruction'
    && entry.entry_type === 'free_account'
    && entry.text === freeAccount
  ))).toBe(true)
  expect(persisted?.statements).toHaveLength(3)
  expect(persisted?.timeline?.contradictions).toContain('MD_TIME_ORDER_CONTRADICTION')
  expect(persisted?.timeline?.unknown_intervals.join('\n')).toContain('точное время неизвестно')
})

test('raw free account passes safety ingress before reconstruction mutation', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Что потерялось?').fill('ключи')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\//)
  const caseId = page.url().split('/cases/')[1]?.split(/[?#]/)[0]
  expect(caseId).toBeTruthy()

  await page.getByTestId('enter-reconstruction').click()
  await expect(page.getByTestId('reconstruction-panel')).toBeVisible()
  await page.getByTestId('free-account-input').fill('Я выключил плиту перед уходом?')
  await page.getByTestId('free-account-submit').click()

  await expect(page.getByTestId('case-safety-route')).toBeVisible()
  const persisted = await storedCase(page, caseId!)
  expect(persisted?.current_mode).toBe('reconstruction')
  expect(persisted?.interaction_journal).toEqual([])
})
