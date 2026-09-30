import { readFileSync } from 'node:fs'
import { expect, test } from '@playwright/test'
import { storedCase } from './helpers'
import { addEvent, addZone, createMobileCase, onboarded } from './mobileHelpers'

test.use({ viewport: { width: 430, height: 844 } })

test('M1 splash and onboarding are shown once, then home', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByTestId('screen-splash')).toContainText('Превращаем фрагменты в проверяемый контекст.')
  await page.getByTestId('splash-start').click()
  await expect(page.getByTestId('screen-onboarding')).toContainText('Ищите потерянное по шагам, а не по кругу')
  await page.getByTestId('onboarding-finish').click()
  await expect(page.getByTestId('screen-home')).toContainText('Что потерялось?')
  await page.reload()
  await expect(page.getByTestId('screen-home')).toBeVisible()
  await expect(page.getByTestId('home-all-cases')).toContainText('0 дел · 0 открыто')
})

test('M2–M6 physical case: reconstruction → explicit search → checks → found and immutable', async ({ page }) => {
  await onboarded(page)
  await page.goto('/new')
  await page.getByTestId('create-reconstruction').click()
  await expect(page.getByRole('alert')).toContainText('Введите название.')

  const caseId = await createMobileCase(page, 'Ключи от машины', 'physical', 'reconstruction')
  await expect(page.getByTestId('screen-case')).toContainText('Реконструкция')

  // M3: verbatim free account, confirmed statement, events with unknown and contradiction.
  const account = '  Вышел из офиса, зашёл в кафе.\nДома ключей уже не было. '
  await page.locator('#free-account').fill(account)
  await page.getByTestId('free-account-save').click()
  await expect(page.getByTestId('free-account-save')).toBeDisabled()
  await page.getByTestId('add-statement').click()
  await page.locator('#statement-text').fill('Ключи были в руке, когда выходил из офиса')
  await page.getByTestId('statement-time').pressSequentially('0800')
  await expect(page.getByTestId('statement-time')).toHaveValue('08:00')
  await page.getByTestId('statement-submit').click()
  await expect(page.getByTestId('statement-card')).toContainText('Воспоминание · 08:00')

  await page.getByTestId('add-event').click()
  await page.locator('#event-title').fill('Ошибка')
  await page.getByTestId('event-time').pressSequentially('2599')
  await page.getByTestId('event-submit').click()
  await expect(page.getByTestId('sheet-event')).toContainText('Укажите время в формате ЧЧ:ММ.')
  await page.getByRole('button', { name: 'Закрыть' }).click()

  await addEvent(page, 'Дорога домой', 'Неизвестное')
  await addEvent(page, 'Офис', 'Точное', '0800')
  await addEvent(page, 'Кафе', 'Точное', '0800')
  await expect(page.getByTestId('timeline').locator('li')).toHaveCount(3)
  await expect(page.getByTestId('timeline').locator('li').last()).toContainText('Время не указано')
  await expect(page.getByTestId('panel-unknown').getByTestId('state-count')).toHaveText('1')
  await expect(page.getByTestId('panel-contradiction').getByTestId('state-count')).toHaveText('1')
  await expect(page.getByTestId('contradiction-line')).toHaveText('08:00: Офис / Кафе')
  await expect(page.getByText('Что вы помните о событии «Дорога домой»?')).toBeVisible()

  let stored = await storedCase(page, caseId)
  expect(stored?.interaction_journal.find(e => e.entry_type === 'free_account')?.text).toBe(account)
  expect(stored?.current_mode).toBe('reconstruction')

  // M4: explicit transition only.
  await page.locator('[data-nav="search"]').click()
  await expect(page.getByTestId('empty-state')).toContainText('Поиск ещё не начат')
  await page.locator('[data-nav="reconstruction"]').click()
  await page.getByTestId('go-search').click()
  await expect(page).toHaveURL(/tab=search/)
  await addZone(page, 'Карман куртки')
  await addZone(page, 'Рюкзак, основной отсек')
  await page.getByTestId('add-zone').click()
  await page.locator('#zone-name').fill('карман  куртки')
  await page.getByTestId('zone-submit').click()
  await expect(page.getByTestId('sheet-zone')).toContainText('Такое место уже есть в списке.')
  await page.getByRole('button', { name: 'Закрыть' }).click()
  await expect(page.getByTestId('next-zone')).toHaveText('Карман куртки')

  // M5: check with method → journal; repeat is marked.
  await page.getByTestId('check-now').click()
  await page.getByRole('radio', { name: 'Проверил руками' }).click()
  await page.getByTestId('check-submit').click()
  await expect(page).toHaveURL(/tab=journal/)
  await expect(page.getByTestId('search-check-card')).toHaveCount(1)
  await page.locator('[data-nav="search"]').click()
  await expect(page.getByTestId('search-progress')).toContainText('1 из 2 мест')
  await expect(page.getByTestId('next-zone')).toHaveText('Рюкзак, основной отсек')
  await page.getByTestId('zone-row').first().click()
  await page.getByRole('radio', { name: 'С фонарём' }).click()
  await page.getByTestId('check-submit').click()
  await expect(page.getByTestId('journal-stats')).toContainText('Повторные')
  await expect(page.getByTestId('search-check-card').first()).toContainText('Проверить повторно')

  // M6: «Нашёл» closes the case; closed case is read-only.
  await page.locator('[data-nav="search"]').click()
  await page.getByTestId('found').click()
  await expect(page.getByRole('dialog')).toContainText('Рюкзак, основной отсек')
  await page.getByTestId('check-submit').click()
  await expect(page.getByTestId('case-outcome')).toContainText('Ключи от машины — найдено')
  stored = await storedCase(page, caseId)
  expect(stored?.lifecycle).toBe('closed_found')
  expect(stored?.search_checks.map(check => check.result)).toEqual(['not_found', 'not_found', 'found'])
  await page.locator('[data-nav="search"]').click()
  await expect(page.getByTestId('add-zone')).toHaveCount(0)
  await expect(page.getByTestId('found')).toHaveCount(0)
  await page.locator('[data-nav="reconstruction"]').click()
  await expect(page.getByTestId('add-event')).toHaveCount(0)
  await expect(page.getByTestId('assistant-card')).toHaveCount(0)
})

test('M7 export → delete → import restores the canonical case', async ({ page }) => {
  await onboarded(page)
  const caseId = await createMobileCase(page, 'Очки', 'physical', 'search')
  await addZone(page, 'Тумбочка')
  await page.getByRole('button', { name: 'Действия с делом' }).click()
  const downloadPromise = page.waitForEvent('download')
  await page.getByTestId('menu-export').click()
  const download = await downloadPromise
  const path = await download.path()
  const exported = JSON.parse(readFileSync(path!, 'utf8'))
  expect(exported.schema).toBe('mind-detective-case/v2')
  expect(exported.case_id).toBe(caseId)

  await page.getByTestId('menu-delete').click()
  await page.getByTestId('confirm-delete').click()
  await expect(page).toHaveURL(/\/cases$/)
  await expect(page.getByTestId('empty-state')).toContainText('Пока нет дел')
  expect(await storedCase(page, caseId)).toBeNull()

  await page.goto('/settings')
  await page.getByTestId('settings-import-file').setInputFiles(path!)
  await expect(page.getByTestId('import-ok')).toBeVisible()
  expect((await storedCase(page, caseId))?.candidates.map(c => c.target)).toEqual(['Тумбочка'])

  await page.getByTestId('settings-import-file').setInputFiles({ name: 'bad.json', mimeType: 'application/json', buffer: Buffer.from('{') })
  await expect(page.getByRole('alert')).toContainText('Не удалось импортировать дело')
})

test('M8 without a server the assistant gives a checklist step labelled research-only', async ({ page }) => {
  let external = 0
  page.on('request', (request) => { if (!request.url().startsWith('http://127.0.0.1')) external += 1 })
  await onboarded(page)
  await createMobileCase(page, 'Наушники', 'physical', 'search')
  await addZone(page, 'Сумка')
  await expect(page.getByTestId('assistant-card')).toContainText('Только исследование')
  await page.getByTestId('assistant-ask').click()
  await expect(page.getByTestId('assistant-proposal')).toHaveAttribute('data-source', 'checklist')
  await expect(page.getByTestId('assistant-proposal-text')).toHaveText('Проверьте: Сумка')
  await expect(page.getByTestId('assistant-proposal')).toContainText('Контрольный список')
  await expect(page.getByTestId('assistant-proposal')).toContainText('Предложение не становится фактом автоматически.')
  expect(external).toBe(0)
})

test('pause and resume from the case menu, cases list filters', async ({ page }) => {
  await onboarded(page)
  const caseId = await createMobileCase(page, 'Зонт', 'physical', 'reconstruction')
  await page.getByRole('button', { name: 'Действия с делом' }).click()
  await page.getByTestId('menu-pause').click()
  expect((await storedCase(page, caseId))?.lifecycle).toBe('paused')
  await page.locator('[data-nav="cases"]').click()
  await expect(page.getByTestId('case-card')).toContainText('Приостановлено')
  await page.getByRole('button', { name: /Пауза/ }).click()
  await expect(page.getByTestId('case-card')).toHaveCount(1)
  await page.getByRole('button', { name: /Завершённые/ }).click()
  await expect(page.getByTestId('case-card')).toHaveCount(0)
})

test('high-risk forgotten action is routed out before a mobile Case is created', async ({ page }) => {
  await onboarded(page)
  await page.goto('/new')
  await page.locator('#new-case-title').fill('Принимал ли я уже таблетки?')
  await page.getByTestId('create-reconstruction').click()
  await expect(page.getByRole('alert')).toContainText('не использует поиск вещей')
  await expect(page).toHaveURL(/\/new$/)
  await page.goto('/cases')
  await expect(page.getByTestId('case-card')).toHaveCount(0)
})
