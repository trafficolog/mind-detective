import { readFile } from 'node:fs/promises'
import { expect, test, type Page } from '@playwright/test'
import { caseFixture, seedCase, storedCase } from './helpers'
import { storedEvaluationEvents, storedEvaluationSessions } from './evaluation-helpers'

async function startStagedCase(page: Page, slot: number, label: string): Promise<{ caseId: string; sessionId: string }> {
  await page.goto('/evaluation')
  await page.getByTestId('evaluation-enrollment-slot').fill(String(slot))
  await page.getByTestId('start-staged-evaluation').click()
  await page.getByTestId('item-label').fill(label)
  await page.getByTestId('start-search').click()
  await expect(page).toHaveURL(/\/cases\//)
  const session = (await storedEvaluationSessions(page))[0]
  expect(session?.case_id).toBeTruthy()
  return { caseId: session!.case_id!, sessionId: session!.evaluation_session_id }
}

test('post-case ratings store one bounded categorical event without free text', async ({ page }) => {
  const { caseId } = await startStagedCase(page, 1, 'rating privacy item')
  await seedCase(page, caseFixture({ case_id: caseId }))
  await page.goto(`/cases/${caseId}`)
  await page.getByRole('button', { name: 'Нашёл' }).click()
  await page.getByTestId('close-unresolved').click()
  await expect(page.getByTestId('case-outcome')).toBeVisible()
  await expect(page.getByTestId('evaluation-ratings')).toBeVisible()
  await expect(page.getByTestId('evaluation-ratings').locator('textarea')).toHaveCount(0)

  await page.getByTestId('evaluation-task-load').selectOption('2')
  await page.getByTestId('evaluation-convenience').selectOption('4')
  await page.getByTestId('save-evaluation-ratings').click()
  await expect(page.getByTestId('evaluation-ratings-saved')).toBeVisible()

  const ratings = (await storedEvaluationEvents(page)).filter(event => event.event === 'post_case_rating')
  expect(ratings).toHaveLength(1)
  expect(ratings[0]?.metadata).toEqual({ task_load: 2, convenience: 4 })
})

test('abandon ends only evaluation participation and reopening Case cannot append operational events', async ({ page }) => {
  const { caseId } = await startStagedCase(page, 1, 'abandon privacy item')
  await seedCase(page, caseFixture({ case_id: caseId }))
  await page.goto(`/cases/${caseId}`)
  await expect(page.getByTestId('evaluation-abandon')).toBeVisible()

  await page.getByTestId('evaluation-abandon').click()
  await expect(page).toHaveURL(/\/evaluation$/)
  const session = (await storedEvaluationSessions(page))[0]
  expect(session?.outcome).toBe('abandoned')
  expect((await storedCase(page, caseId))?.lifecycle).toBe('active')
  expect((await storedEvaluationEvents(page)).filter(event => event.event === 'case_abandoned')).toHaveLength(1)

  const eventCount = (await storedEvaluationEvents(page)).length
  await page.goto(`/cases/${caseId}`)
  await expect(page.getByTestId('case-page')).toBeVisible()
  await expect.poll(async () => (await storedEvaluationEvents(page)).length).toBe(eventCount)
})

test('staged observer stores exactly the fixed proposal safety booleans', async ({ page }) => {
  const { caseId, sessionId } = await startStagedCase(page, 1, 'observer privacy item')
  await seedCase(page, caseFixture({ case_id: caseId }))
  await page.goto(`/cases/${caseId}`)
  await expect(page.getByTestId('next-action-target')).toBeVisible()
  expect((await storedEvaluationEvents(page)).some(event => event.event === 'next_action_shown')).toBe(true)

  await page.goto(`/evaluation/observer/${sessionId}`)
  await expect(page.getByTestId('evaluation-observer')).toBeVisible()
  await page.getByTestId('safety-leading-suggestion').check()
  await page.getByTestId('save-safety-annotation').click()

  const annotation = (await storedEvaluationEvents(page)).find(event => event.event === 'proposal_safety_annotation')
  expect(annotation).toBeTruthy()
  expect(Object.keys(annotation!.metadata).sort()).toEqual([
    'critical_forgetting_diagnosis',
    'critical_invented_recollection',
    'critical_location_assertion',
    'critical_unsafe_action',
    'false_confidence',
    'leading_suggestion',
    'proposal_id',
    'unsupported_fact',
  ].sort())
  expect(annotation?.metadata.leading_suggestion).toBe(true)
  expect(annotation?.metadata.unsupported_fact).toBe(false)
})

test('S4 observer stores four booleans and the derived handoff score', async ({ page }) => {
  const { sessionId } = await startStagedCase(page, 4, 'handoff privacy item')
  await page.goto(`/evaluation/observer/${sessionId}`)
  await expect(page.getByTestId('handoff-rubric')).toBeVisible()
  await page.getByTestId('handoff-mode-restored').check()
  await page.getByTestId('handoff-prior-checks-preserved').check()
  await page.getByTestId('handoff-next-action-coherent').check()
  await page.getByTestId('save-handoff-rubric').click()

  const rubric = (await storedEvaluationEvents(page)).find(event => event.event === 'handoff_rubric')
  expect(rubric?.metadata).toEqual({
    mode_restored: true,
    prior_checks_preserved: true,
    journal_continuity: false,
    next_action_coherent: true,
    handoff_score: 3,
  })
})

test('explicit JSON and CSV evaluation exports contain no Case content and issue no network requests', async ({ page }) => {
  const privateItem = 'секретная вещь для проверки приватности'
  const privateTarget = 'секретное место для проверки приватности'
  const privateReason = 'только содержимое Case для теста приватности'
  const { caseId } = await startStagedCase(page, 1, privateItem)
  await seedCase(page, caseFixture({
    case_id: caseId,
    item_label: privateItem,
    candidates: [{
      id: 'candidate-1',
      target: privateTarget,
      source: 'system',
      status: 'unchecked',
      priority_band: 'primary',
      rank_reason: privateReason,
      evidence_ids: [],
    }],
  }))
  await page.goto(`/cases/${caseId}`)
  await expect(page.getByTestId('next-action-target')).toHaveText(privateTarget)
  await page.goto('/evaluation')
  await expect(page.getByTestId('evaluation-export-actions')).toBeVisible()

  const networkRequests: string[] = []
  page.on('request', request => networkRequests.push(request.url()))

  const jsonPromise = page.waitForEvent('download')
  await page.getByTestId('export-evaluation-json').click()
  const jsonDownload = await jsonPromise
  const jsonPath = await jsonDownload.path()
  expect(jsonPath).toBeTruthy()
  const json = await readFile(jsonPath!, 'utf8')

  const csvPromise = page.waitForEvent('download')
  await page.getByTestId('export-evaluation-csv').click()
  const csvDownload = await csvPromise
  const csvPath = await csvDownload.path()
  expect(csvPath).toBeTruthy()
  const csv = await readFile(csvPath!, 'utf8')

  for (const exported of [json, csv]) {
    expect(exported).not.toContain(privateItem)
    expect(exported).not.toContain(privateTarget)
    expect(exported).not.toContain(privateReason)
    expect(exported).not.toContain('interaction_journal')
    expect(exported).not.toContain('raw_model_output')
  }
  expect(networkRequests).toEqual([])
})
