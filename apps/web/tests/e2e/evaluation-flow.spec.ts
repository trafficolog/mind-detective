import { expect, test, type Page } from '@playwright/test'
import { candidate, caseFixture, searchCheck, seedCase } from './helpers'
import { storedEvaluationEvents, storedEvaluationSessions } from './evaluation-helpers'

async function startStagedCase(page: Page, slot: number, label: string): Promise<string> {
  await page.goto('/evaluation')
  await page.getByTestId('evaluation-enrollment-slot').fill(String(slot))
  await page.getByTestId('start-staged-evaluation').click()
  await page.getByTestId('item-label').fill(label)
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\//)
  const session = (await storedEvaluationSessions(page))[0]
  expect(session?.case_id).toBeTruthy()
  return session!.case_id!
}

test('ordinary Case creation does not create evaluation assignment or session events', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByTestId('offline-route-ready')).toBeVisible()
  await page.getByTestId('item-label').fill('обычные ключи')
  await page.getByTestId('start-search').click()
  await expect(page.getByTestId('case-page')).toBeVisible()

  expect(await storedEvaluationSessions(page)).toEqual([])
  expect(await storedEvaluationEvents(page)).toEqual([])
})

test('staged B assignment is bound before Case navigation and survives reload', async ({ page }) => {
  await page.goto('/evaluation')
  await expect(page.getByTestId('evaluation-page')).toBeVisible()
  expect(await storedEvaluationSessions(page)).toEqual([])

  await page.getByTestId('evaluation-enrollment-slot').fill('1')
  await page.getByTestId('start-staged-evaluation').click()
  await expect(page.getByTestId('evaluation-arm')).toHaveText('Arm B')
  await expect(page.getByTestId('evaluation-scenario')).toContainText('S1')

  await page.getByTestId('item-label').fill('staged ключи')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\//)
  await expect(page.getByTestId('case-page')).toBeVisible()

  const sessions = await storedEvaluationSessions(page)
  expect(sessions).toHaveLength(1)
  expect(sessions[0]?.arm).toBe('B')
  expect(sessions[0]?.case_id).toBeTruthy()
  expect(sessions[0]?.started_at).toBeTruthy()
  expect((await storedEvaluationEvents(page)).filter(event => event.event === 'case_started')).toHaveLength(1)
  await expect(page.getByTestId('provider-disclosure')).toHaveCount(0)

  await page.reload()
  await expect(page.getByTestId('case-page')).toBeVisible()
  await expect(page.getByTestId('provider-disclosure')).toHaveCount(0)
  const reloaded = await storedEvaluationSessions(page)
  expect(reloaded[0]?.evaluation_session_id).toBe(sessions[0]?.evaluation_session_id)
  expect(reloaded[0]?.arm).toBe('B')
})

test('staged C assignment overrides checklist build arm and survives reload', async ({ page }) => {
  await page.goto('/evaluation')
  await page.getByTestId('evaluation-enrollment-slot').fill('3')
  await page.getByTestId('start-staged-evaluation').click()
  await expect(page.getByTestId('evaluation-arm')).toHaveText('Arm C')
  await expect(page.getByTestId('evaluation-scenario')).toContainText('S3')

  await page.getByTestId('item-label').fill('assistant staged вещь')
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\//)
  await expect(page.getByTestId('provider-disclosure')).toBeVisible()

  const session = (await storedEvaluationSessions(page))[0]
  expect(session?.arm).toBe('C')
  await page.reload()
  await expect(page.getByTestId('provider-disclosure')).toBeVisible()
  expect((await storedEvaluationSessions(page))[0]?.evaluation_session_id).toBe(session?.evaluation_session_id)
})

test('B session records linked useful-action instrumentation and finishes atomically', async ({ page }) => {
  const caseId = await startStagedCase(page, 1, 'instrumented keys')
  await seedCase(page, caseFixture({ case_id: caseId }))
  await page.goto(`/cases/${caseId}`)
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')

  await page.getByTestId('mark-checked').click()
  await expect(page.getByTestId('progress-checked')).toContainText('1')
  await page.getByTestId('found-case').click()
  await page.getByTestId('found-context').selectOption('elsewhere_unplanned')
  await page.getByTestId('close-found').click()
  await expect(page.getByTestId('case-outcome')).toContainText('найдено')

  const events = await storedEvaluationEvents(page)
  const chronological = [...events].sort((left, right) => left.at.localeCompare(right.at) || left.event_id.localeCompare(right.event_id))
  expect(chronological.map(event => event.event)).toEqual([
    'case_started',
    'next_action_shown',
    'check_started',
    'check_finished',
    'next_action_shown',
    'found',
  ])

  const shown = chronological.find(event => event.event === 'next_action_shown')
  const started = chronological.find(event => event.event === 'check_started')
  const finished = chronological.find(event => event.event === 'check_finished')
  const reshown = chronological.filter(event => event.event === 'next_action_shown')[1]
  expect(shown?.metadata.proposal_id).toBeTruthy()
  expect(started?.metadata.proposal_id).toBe(shown?.metadata.proposal_id)
  expect(finished?.metadata.proposal_id).toBe(shown?.metadata.proposal_id)
  expect(shown?.metadata.candidate_id).toBe('candidate-1')
  expect(started?.metadata.candidate_id).toBe('candidate-1')
  expect(reshown?.metadata.candidate_id).toBe('candidate-1')
  expect(reshown?.metadata.proposal_id).not.toBe(shown?.metadata.proposal_id)
  expect(chronological.at(-1)?.metadata.found_context).toBe('elsewhere_unplanned')

  const session = (await storedEvaluationSessions(page))[0]
  expect(session?.outcome).toBe('found')
  expect(session?.ended_at).toBeTruthy()
})

test('duplicate check is derived from canonical prior evidence', async ({ page }) => {
  const caseId = await startStagedCase(page, 1, 'duplicate keys')
  await seedCase(page, caseFixture({
    case_id: caseId,
    updated_at: '2026-09-10T07:01:10Z',
    candidates: [candidate('candidate-1', 'карманы куртки', 'partial')],
    search_checks: [searchCheck('prior-check', 'candidate-1', 'карманы куртки', 'reported_check')],
  }))
  await page.goto(`/cases/${caseId}`)
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')
  await expect(page.getByTestId('check-quality-dialog')).toBeVisible()
  await page.getByRole('button', { name: 'Не сейчас' }).click()
  await expect(page.getByTestId('check-quality-dialog')).toHaveCount(0)
  await page.getByTestId('mark-checked').click()

  await expect.poll(async () => {
    const duplicate = (await storedEvaluationEvents(page)).find(event => event.event === 'duplicate_check_detected')
    return duplicate?.metadata.candidate_id
  }).toBe('candidate-1')

  const events = await storedEvaluationEvents(page)
  const duplicate = events.find(event => event.event === 'duplicate_check_detected')
  const started = events.find(event => event.event === 'check_started')
  expect(duplicate?.metadata.proposal_id).toBe(started?.metadata.proposal_id)
})

test('C transport failure records fallback without changing assigned arm', async ({ page }) => {
  const caseId = await startStagedCase(page, 3, 'fallback keys')
  await seedCase(page, caseFixture({ case_id: caseId }))
  await page.route('**/api/v1/proposal/next', route => route.abort('failed'))
  await page.goto(`/cases/${caseId}`)

  await expect(page.getByTestId('assistant-offline-fallback')).toBeVisible()
  await expect(page.getByTestId('next-action-target')).toHaveText('карманы куртки')
  const events = await storedEvaluationEvents(page)
  expect(events.some(event => event.event === 'assistant_offline_fallback')).toBe(true)
  expect(events.some(event => event.event === 'next_action_shown')).toBe(true)
  expect((await storedEvaluationSessions(page))[0]?.arm).toBe('C')
})
