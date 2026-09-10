import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { expect, test } from '@playwright/test'
import { caseFixture, seedCase, storedCase } from './helpers'

test('generated PWA precaches shell assets without API case or background-sync data', async () => {
  const output = resolve(process.cwd(), '.output/public')
  const worker = readFileSync(resolve(output, 'sw.js'), 'utf8')
  const manifest = JSON.parse(readFileSync(resolve(process.cwd(), 'public/manifest.webmanifest'), 'utf8')) as {
    display?: string
    start_url?: string
  }

  expect(manifest.display).toBe('standalone')
  expect(manifest.start_url).toBe('/')
  expect(worker).toContain('index.html')
  expect(worker).not.toMatch(/BackgroundSyncPlugin|workbox-background-sync|backgroundSync/)
  expect(worker).not.toMatch(/"url":"\/api\//)
  expect(worker).not.toMatch(/mind-detective-case\/v2|item_label|interaction_journal|evaluation-export/)
})

test('failed offline mutation leaves canonical case unchanged and retry reuses the same envelope', async ({ page }) => {
  const caseValue = caseFixture()
  const attempts: unknown[] = []
  let failFirst = true

  await page.route('**/api/v1/case/command', async (route) => {
    attempts.push(route.request().postDataJSON())
    if (failFirst) {
      failFirst = false
      await route.abort('internetdisconnected')
      return
    }
    await route.continue()
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)
  await page.getByTestId('mark-checked').click()

  await expect(page.getByTestId('command-error')).toBeVisible()
  await expect(page.getByTestId('progress-checked')).toContainText('0')
  expect((await storedCase(page, caseValue.case_id))?.search_checks).toHaveLength(0)

  await page.getByRole('button', { name: 'Повторить ту же команду' }).click()
  await expect(page.getByTestId('progress-checked')).toContainText('1')
  expect((await storedCase(page, caseValue.case_id))?.search_checks).toHaveLength(1)
  expect(attempts).toHaveLength(2)
  expect(attempts[1]).toEqual(attempts[0])
})
