import { describe, expect, it } from 'vitest'
import {
  caseCardView, caseMeta, caseNumbers, caseStats, caseStatus, confirmedStatements, filterCases, formatCaseNumber,
  formatUpdated, freeAccountText, homeSummary, itemKind, journalStats, journalView, listFilters, nextZone, plural,
  recStats, searchProgress, timelineView, zonesView,
} from '../../app/lib/mobile/viewModel'
import { CaseBuilder } from './support/mobileCases'

const NOW = new Date('2026-09-30T12:00:00Z')

function keysCase(): CaseBuilder {
  return CaseBuilder.create('Ключи от машины')
    .reconstruction()
    .freeAccount('Вышел из офиса, зашёл в кафе, потом сел в машину и доехал домой. Дома ключей уже не было.')
    .statement('recollection', 'Ключи были в руке, когда выходил из офиса', '08:00')
    .statement('habit', 'Обычно кладу ключи в карман куртки')
    .events([['Офис', 'exact', '08:00'], ['Кафе', 'approximate', '08:40'], ['Дорога домой', 'unknown', null]])
    .search()
    .target('Карман куртки').target('Рюкзак, основной отсек').target('Полка в прихожей')
    .check('Карман куртки', 'hand')
}

describe('mobile view model (derived presentation of canonical Case v2)', () => {
  it('reads item kind, free account text and its latest revision', () => {
    const c = keysCase()
    expect(itemKind(c.value)).toBe('physical')
    expect(freeAccountText(c.value)).toContain('Дома ключей уже не было.')
    c.run('revise_free_account', { entry_id: 'fa-rev', text: 'Новый рассказ' })
    expect(freeAccountText(c.value)).toBe('Новый рассказ')
    expect(itemKind(CaseBuilder.create('Фото', 'digital').value)).toBe('digital')
    expect(freeAccountText(CaseBuilder.create().value)).toBe('')
  })

  it('shows confirmed statements without search targets and counts reconstruction states', () => {
    const c = keysCase().statement('hypothesis', 'Может, в машине')
    const statements = confirmedStatements(c.value)
    expect(statements.map(s => s.text)).toEqual([
      'Ключи были в руке, когда выходил из офиса', 'Обычно кладу ключи в карман куртки', 'Может, в машине',
    ])
    expect(statements[0]).toMatchObject({ sub: 'Воспоминание · 08:00', variant: 'confirmed', chip: 'confirmed' })
    expect(statements[2]).toMatchObject({ variant: 'default', chip: 'hypothesis' })
    expect(recStats(c.value)).toEqual({ confirmed: 2, unknown: 1, contradiction: 0 })
  })

  it('T07 sorts timeline by time with unknown events last and derives connectors', () => {
    const c = CaseBuilder.create().reconstruction().freeAccount()
      .events([['B', 'unknown', null], ['C', 'exact', '09:30'], ['A', 'exact', '08:00']])
    const view = timelineView(c.value)
    expect(view.items.map(i => i.title)).toEqual(['A', 'C', 'B'])
    expect(view.items.map(i => i.time)).toEqual(['08:00', '09:30', 'Время не указано'])
    expect(view.items.map(i => i.connector)).toEqual(['confirmed', 'unknown', 'none'])
    expect(view.firstUnknownTitle).toBe('B')
  })

  it('T08 marks same-exact-time events as contradictions from kernel output', () => {
    const c = CaseBuilder.create().reconstruction().freeAccount()
      .events([['Офис', 'exact', '08:00'], ['Кафе', 'exact', '08:00'], ['Дом', 'approximate', '09:00']])
    const view = timelineView(c.value)
    expect(view.items.filter(i => i.status === 'contradiction').map(i => i.title)).toEqual(['Офис', 'Кафе'])
    expect(view.contradictions).toEqual(['08:00: Офис / Кафе'])
    expect(view.items[2]).toMatchObject({ status: 'confirmed', detail: 'Примерное время' })
  })

  it('T12 T13 T14 zones, progress, next zone and repeat checks', () => {
    const c = keysCase()
    expect(searchProgress(c.value)).toEqual({ done: 1, total: 3 })
    expect(nextZone(c.value)?.name).toBe('Рюкзак, основной отсек')
    const zones = zonesView(c.value)
    expect(zones.map(z => [z.n, z.name, z.label, z.icon])).toEqual([
      ['1', 'Карман куртки', 'Проверил руками · не нашёл', 'circle-check'],
      ['2', 'Рюкзак, основной отсек', 'Не проверено', 'circle'],
      ['3', 'Полка в прихожей', 'Не проверено', 'circle'],
    ])
    c.check('Рюкзак, основной отсек', 'opened', 'partial')
    expect(searchProgress(c.value)).toEqual({ done: 1, total: 3 })
    expect(nextZone(c.value)?.name).toBe('Рюкзак, основной отсек')
    c.check('карман куртки', 'flashlight')
    const journal = journalView(c.value, NOW)
    expect(journal.map(k => [k.place, k.repeat, k.result])).toEqual([
      ['карман куртки', true, 'repeat'],
      ['Рюкзак, основной отсек', false, 'incomplete'],
      ['Карман куртки', false, 'not-found'],
    ])
    expect(journal[0]).toMatchObject({ method: 'flashlight', methodKey: 'flashlight' })
    expect(journalStats(c.value)).toEqual({ total: 3, repeats: 1, partial: 1 })
  })

  it('next zone is empty for closed cases', () => {
    const c = keysCase().run('close_unresolved', { outcome: {} })
    expect(nextZone(c.value)).toBeNull()
  })

  it('T18 case status chip follows lifecycle and mode', () => {
    expect(caseStatus(CaseBuilder.create().reconstruction().value)).toBe('reconstruction')
    expect(caseStatus(CaseBuilder.create().value)).toBe('reconstruction')
    expect(caseStatus(CaseBuilder.create().search().value)).toBe('active-search')
    expect(caseStatus(CaseBuilder.create().search().run('pause').value)).toBe('paused')
    expect(caseStatus(CaseBuilder.create().search().run('close_found', { outcome: {} }).value)).toBe('found')
    expect(caseStatus(CaseBuilder.create().search().run('close_unresolved', { outcome: {} }).value)).toBe('closed')
  })

  it('T02 case numbers follow creation order', () => {
    const a = CaseBuilder.create('A', 'physical', 'case-a', '2026-09-28T10:00:00Z').value
    const b = CaseBuilder.create('B', 'physical', 'case-b', '2026-09-29T10:00:00Z').value
    const numbers = caseNumbers([b, a])
    expect(numbers.get('case-a')).toBe(1)
    expect(numbers.get('case-b')).toBe(2)
    expect(formatCaseNumber(1)).toBe('#001')
    expect(formatCaseNumber(42)).toBe('#042')
  })

  it('formats Russian plurals, updated time and meta', () => {
    expect([1, 2, 5, 11, 21, 22].map(n => plural(n, 'дело', 'дела', 'дел'))).toEqual(['1 дело', '2 дела', '5 дел', '11 дел', '21 дело', '22 дела'])
    const local = new Date(NOW)
    local.setHours(9, 5, 0, 0)
    expect(formatUpdated(local.toISOString(), NOW)).toBe('Сегодня, 09:05')
    const earlier = new Date(2026, 8, 12, 18, 30)
    expect(formatUpdated(earlier.toISOString(), NOW)).toBe('12.09, 18:30')
    expect(caseMeta(keysCase().value)).toBe('3 события · 1 проверка')
  })

  it('builds case cards, filters, stats and home summary', () => {
    const keys = keysCase().value
    const photo = CaseBuilder.create('Фото', 'digital', 'case-p', '2026-09-30T09:00:00Z').reconstruction().value
    const closed = CaseBuilder.create('Очки', 'physical', 'case-c', '2026-09-20T09:00:00Z').search().run('close_found', { outcome: {} }).value
    const all = [keys, photo, closed]
    const card = caseCardView(keys, 2, NOW)
    expect(card).toMatchObject({ title: 'Ключи от машины', caseId: '#002', status: 'active-search', place: 'Кафе', icon: 'key-round' })
    expect(card.counts).toEqual(['1 из 3 зон', '1 проверка', '1 неизвестный интервал'])
    expect(caseCardView(photo, 1, NOW).icon).toBe('image')
    expect(listFilters(all).map(f => [f.value, f.label, f.count])).toEqual([
      ['all', 'Все', 3], ['active', 'Активные', 2], ['paused', 'Пауза', 0], ['done', 'Завершённые', 1],
    ])
    expect(filterCases(all, 'done').map(c => c.case_id)).toEqual(['case-c'])
    expect(caseStats(all)).toEqual([
      { label: 'В поиске', n: 1 }, { label: 'Восстановление', n: 1 }, { label: 'Завершено', n: 1 },
    ])
    const home = homeSummary(all)
    expect(home.listSub).toBe('3 дела · 2 открыто')
    expect(home.active?.case_id).toBe('case-1')
  })

  it('T21 view functions never mutate the canonical case', () => {
    const c = keysCase().value
    const frozen = structuredClone(c)
    timelineView(c); zonesView(c); journalView(c, NOW); caseCardView(c, 1, NOW); confirmedStatements(c)
    expect(c).toEqual(frozen)
  })
})
