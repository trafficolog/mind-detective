import { expect, test } from '@playwright/test'
import { storedEvaluationEvents, storedEvaluationSessions } from './evaluation-helpers'

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
