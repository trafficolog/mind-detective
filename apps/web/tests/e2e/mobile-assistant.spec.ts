import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'
import { addZone, createMobileCase, onboarded } from './mobileHelpers'

test.use({ viewport: { width: 430, height: 844 } })

const N8N = 'https://n8n.example.test'
const serverSettings = {
  'md.mobile.assistant': '1',
  'md.mobile.server': JSON.stringify({ url: N8N, token: 'secret-token' }),
}

test('M10 n8n propose → guarded assistant proposal → explicit add to the check list', async ({ page }) => {
  const prompts: string[] = []
  await page.route(`${N8N}/webhook/md-propose`, async (route) => {
    expect(route.request().headers().authorization).toBe('Bearer secret-token')
    const body = JSON.parse(route.request().postData() ?? '{}') as { prompt: string }
    expect(Object.keys(body)).toEqual(['prompt'])
    prompts.push(body.prompt)
    await route.fulfill({ json: { text: '```json {"kind":"check","text":"Проверьте карман пальто","place":"Карман пальто"} ```' }, headers: { 'access-control-allow-origin': '*' } })
  })
  await onboarded(page, serverSettings)
  await page.goto('/settings')
  await expect(page.getByTestId('server-mode')).toContainText('Подключено')
  await expect(page.getByTestId('assistant-toggle')).toHaveText('Отключить онлайн-ассистента')

  const caseId = await createMobileCase(page, 'Ключи', 'physical', 'reconstruction')
  await page.locator('#free-account').fill('секретный свободный рассказ')
  await page.getByTestId('free-account-save').click()
  await page.getByTestId('go-search').click()
  await addZone(page, 'Сумка')
  await page.getByTestId('assistant-ask').click()
  await expect(page.getByTestId('assistant-proposal')).toHaveAttribute('data-source', 'assistant')
  await expect(page.getByTestId('assistant-proposal')).toContainText('Ассистент · только исследование')
  expect(prompts).toHaveLength(1)
  expect(prompts[0]).not.toContain('секретный')
  expect((await storedCase(page, caseId))?.candidates).toHaveLength(1)

  await page.getByTestId('assistant-accept').click()
  await expect.poll(async () => (await storedCase(page, caseId))?.candidates.map(c => c.target)).toEqual(['Сумка', 'Карман пальто'])
})

test('M10 unavailable or rejected n8n answer falls back to the local checklist', async ({ page }) => {
  let calls = 0
  await page.route(`${N8N}/webhook/md-propose`, async (route) => {
    calls += 1
    if (calls === 1) {
      await route.fulfill({ status: 503, body: 'down', headers: { 'access-control-allow-origin': '*' } })
      return
    }
    await route.fulfill({ json: { text: '{"kind":"check","text":"Скорее всего в машине","place":"Машина"}' }, headers: { 'access-control-allow-origin': '*' } })
  })
  await onboarded(page, serverSettings)
  await createMobileCase(page, 'Кошелёк', 'physical', 'search')
  await addZone(page, 'Куртка')
  await page.getByTestId('assistant-ask').click()
  await expect(page.getByTestId('assistant-proposal')).toHaveAttribute('data-source', 'fallback')
  await expect(page.getByTestId('assistant-proposal')).toContainText('Ассистент недоступен — использован локальный контрольный список.')
  await page.getByTestId('assistant-ask').click()
  await expect(page.getByTestId('assistant-proposal')).toContainText('Ответ ассистента не прошёл проверку')
  await expect(page.getByTestId('assistant-proposal-text')).toHaveText('Проверьте: Куртка')
})
