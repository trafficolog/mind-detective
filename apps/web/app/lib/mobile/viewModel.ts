// Derived presentation of a canonical Case v2 for the Glass Modern mobile shell.
// Pure read-only functions: no Case mutation, no semantics beyond what the generated kernel stored (ADR 009/015/016).
import { item_kind_json } from '../../generated/localExecution'
import type { CaseV2, SearchCheckV2, TimelineEventV2 } from '../api/contracts'
import { dsMethodKey, methodLabel, resultLabel, STATEMENT_TYPES, vocab, type ItemKind } from './vocab'

export type CaseStatusKey = 'reconstruction' | 'active-search' | 'paused' | 'found' | 'closed'
export type TimelineStatus = 'confirmed' | 'unknown' | 'contradiction'
export type CaseFilter = 'all' | 'active' | 'paused' | 'done'

const SAME_TIME_PREFIX = 'MD_TIME_SAME_EXACT_TIME:'
const CONTRADICTION_TEXT: Record<string, string> = {
  MD_TIME_ORDER_CONTRADICTION: 'Последний подтверждённый момент указан позже, чем момент, когда заметили пропажу',
  MD_TIME_REFERENCE_MISSING: 'Ссылка на сведение не найдена',
  MD_TIME_INVALID_TIMESTAMP: 'Время указано в неподдерживаемом формате',
}

export function normalizeLabel(value: string): string {
  return value.toLowerCase().replaceAll('ё', 'е').split(/\s+/).filter(Boolean).join(' ')
}

export function plural(n: number, one: string, few: string, many: string): string {
  const m100 = n % 100
  const m10 = n % 10
  const word = m100 > 10 && m100 < 20 ? many : m10 === 1 ? one : m10 > 1 && m10 < 5 ? few : many
  return `${n} ${word}`
}

const pad = (value: number): string => String(value).padStart(2, '0')

export function formatUpdated(iso: string, now: Date = new Date()): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const time = `${pad(date.getHours())}:${pad(date.getMinutes())}`
  return date.toDateString() === now.toDateString()
    ? `Сегодня, ${time}`
    : `${pad(date.getDate())}.${pad(date.getMonth() + 1)}, ${time}`
}

const CLOCK = /^\d{2}:\d{2}$/

function eventTimeLabel(value: string): string {
  if (CLOCK.test(value)) return value
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}, ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function eventSortKey(value: string): number {
  if (CLOCK.test(value)) return Number(value.slice(0, 2)) * 60 + Number(value.slice(3, 5))
  const time = Date.parse(value)
  return Number.isNaN(time) ? Number.MAX_SAFE_INTEGER : time / 60_000
}

export function itemKind(caseValue: CaseV2): ItemKind {
  return item_kind_json(caseValue as unknown as Record<string, unknown>) === 'digital' ? 'digital' : 'physical'
}

export function isClosed(caseValue: CaseV2): boolean {
  return caseValue.lifecycle === 'closed_found' || caseValue.lifecycle === 'closed_unresolved' || caseValue.lifecycle === 'deleted'
}

export function freeAccountText(caseValue: CaseV2): string {
  let text = ''
  for (const entry of caseValue.interaction_journal) {
    if (entry.author === 'user' && (entry.entry_type === 'free_account' || entry.entry_type === 'free_account_revision')) {
      text = entry.text
    }
  }
  return text
}

export function hasFreeAccount(caseValue: CaseV2): boolean {
  return caseValue.interaction_journal.some(entry => entry.author === 'user' && entry.entry_type === 'free_account')
}

export interface StatementView {
  id: string
  text: string
  type: string
  sub: string
  variant: 'confirmed' | 'default'
  chip: 'confirmed' | 'hypothesis'
}

export function confirmedStatements(caseValue: CaseV2): StatementView[] {
  return caseValue.statements
    .filter(statement => statement.statement_type !== 'search_suggestion')
    .map((statement) => {
      const hypothesis = statement.statement_type === 'hypothesis'
      const typeLabel = (STATEMENT_TYPES as Record<string, string>)[statement.statement_type] ?? statement.statement_type
      return {
        id: statement.id,
        text: statement.original_text,
        type: statement.statement_type,
        sub: [typeLabel, statement.event_time ? eventTimeLabel(statement.event_time) : '', statement.limitations.join(', ')]
          .filter(Boolean)
          .join(' · '),
        variant: hypothesis ? 'default' : 'confirmed',
        chip: hypothesis ? 'hypothesis' : 'confirmed',
      }
    })
}

export function recStats(caseValue: CaseV2): { confirmed: number, unknown: number, contradiction: number } {
  return {
    confirmed: caseValue.statements.filter(s => s.statement_type !== 'hypothesis' && s.statement_type !== 'search_suggestion').length,
    unknown: caseValue.timeline?.unknown_intervals.length ?? 0,
    contradiction: caseValue.timeline?.contradictions.length ?? 0,
  }
}

export interface TimelineItemView {
  id: string
  time: string
  title: string
  detail?: string
  status: TimelineStatus
  connector: TimelineStatus | 'none'
}

export interface TimelineView {
  items: TimelineItemView[]
  contradictions: string[]
  unknownCount: number
  firstUnknownTitle: string | null
}

function isKnown(event: TimelineEventV2): event is TimelineEventV2 & { event_time: string } {
  return event.time_precision !== 'unknown' && typeof event.event_time === 'string'
}

export function timelineView(caseValue: CaseV2): TimelineView {
  const events = caseValue.timeline?.events ?? []
  const codes = caseValue.timeline?.contradictions ?? []
  const conflictingTimes = new Set(codes.filter(code => code.startsWith(SAME_TIME_PREFIX)).map(code => code.slice(SAME_TIME_PREFIX.length)))
  const known = events.filter(isKnown)
    .map((event, index) => ({ event, index }))
    .sort((a, b) => eventSortKey(a.event.event_time) - eventSortKey(b.event.event_time) || a.index - b.index)
    .map(({ event }) => event)
  const unknown = events.filter(event => !isKnown(event))
  const statusOf = (event: TimelineEventV2): TimelineStatus => {
    if (!isKnown(event)) return 'unknown'
    return event.time_precision === 'exact' && conflictingTimes.has(event.event_time) ? 'contradiction' : 'confirmed'
  }
  const ordered = [...known, ...unknown]
  const statuses = ordered.map(statusOf)
  const items = ordered.map((event, index): TimelineItemView => ({
    id: event.id,
    time: isKnown(event) ? eventTimeLabel(event.event_time) : 'Время не указано',
    title: event.label,
    detail: event.time_precision === 'approximate' ? 'Примерное время' : undefined,
    status: statuses[index]!,
    connector: index === ordered.length - 1 ? 'none' : statuses[index + 1] === 'unknown' ? 'unknown' : statuses[index]!,
  }))
  const contradictions = codes.map((code) => {
    if (!code.startsWith(SAME_TIME_PREFIX)) return CONTRADICTION_TEXT[code] ?? code
    const time = code.slice(SAME_TIME_PREFIX.length)
    const titles = events.filter(e => e.time_precision === 'exact' && e.event_time === time).map(e => e.label)
    return `${eventTimeLabel(time)}: ${titles.join(' / ')}`
  })
  return {
    items,
    contradictions,
    unknownCount: caseValue.timeline?.unknown_intervals.length ?? 0,
    firstUnknownTitle: unknown[0]?.label ?? null,
  }
}

export interface ZoneView {
  id: string
  n: string
  name: string
  label: string
  done: boolean
  icon: 'circle-check' | 'circle'
}

function checksForCandidate(caseValue: CaseV2, candidateId: string, target: string): SearchCheckV2[] {
  const key = normalizeLabel(target)
  return caseValue.search_checks.filter(check =>
    check.based_on.includes(candidateId) || (check.based_on.length === 0 && normalizeLabel(check.target) === key))
}

export function zonesView(caseValue: CaseV2): ZoneView[] {
  return caseValue.candidates.map((candidate, index) => {
    const checks = checksForCandidate(caseValue, candidate.id, candidate.target)
    const last = checks[checks.length - 1]
    const done = candidate.check_state === 'checked'
    return {
      id: candidate.id,
      n: String(index + 1),
      name: candidate.target,
      label: last ? `${methodLabel(last.method)} · ${resultLabel(last.result).toLowerCase()}` : 'Не проверено',
      done,
      icon: done ? 'circle-check' : 'circle',
    }
  })
}

export function searchProgress(caseValue: CaseV2): { done: number, total: number } {
  return {
    done: caseValue.candidates.filter(candidate => candidate.check_state === 'checked').length,
    total: caseValue.candidates.length,
  }
}

export function nextZone(caseValue: CaseV2): ZoneView | null {
  if (isClosed(caseValue)) return null
  return zonesView(caseValue).find(zone => !zone.done) ?? null
}

export function findCandidateId(caseValue: CaseV2, target: string): string | null {
  const key = normalizeLabel(target)
  return caseValue.candidates.find(candidate => normalizeLabel(candidate.target) === key)?.id ?? null
}

export interface CheckView {
  id: string
  place: string
  method: string
  methodKey: string
  methodLabel: string
  time: string
  result: 'found' | 'incomplete' | 'repeat' | 'not-found'
  note: string
  repeat: boolean
  sub: string
  resultIcon: string
}

export function journalView(caseValue: CaseV2, now: Date = new Date()): CheckView[] {
  const checks = caseValue.search_checks
  const views = checks.map((check, index): CheckView => {
    const key = normalizeLabel(check.target)
    const repeat = checks.slice(0, index).some(previous => normalizeLabel(previous.target) === key)
    const incomplete = check.result === 'partial' || check.result === 'inaccessible'
    const result = check.result === 'found' ? 'found' : incomplete ? 'incomplete' : repeat ? 'repeat' : 'not-found'
    const time = formatUpdated(check.completed_at ?? check.started_at, now)
    return {
      id: check.id,
      place: check.target,
      method: dsMethodKey(check.method),
      methodKey: check.method,
      methodLabel: methodLabel(check.method),
      time,
      result,
      note: check.notes.join(' '),
      repeat,
      sub: [methodLabel(check.method), resultLabel(check.result).toLowerCase(), repeat ? 'повторно' : '', time].filter(Boolean).join(' · '),
      resultIcon: check.result === 'found' ? 'circle-check' : incomplete ? 'circle-dashed' : 'circle-x',
    }
  })
  return views.reverse()
}

export function journalStats(caseValue: CaseV2): { total: number, repeats: number, partial: number } {
  const views = journalView(caseValue)
  return {
    total: views.length,
    repeats: views.filter(view => view.repeat).length,
    partial: caseValue.search_checks.filter(check => check.result === 'partial' || check.result === 'inaccessible').length,
  }
}

export function caseStatus(caseValue: CaseV2): CaseStatusKey {
  if (caseValue.lifecycle === 'closed_found') return 'found'
  if (caseValue.lifecycle === 'closed_unresolved' || caseValue.lifecycle === 'deleted') return 'closed'
  if (caseValue.lifecycle === 'paused') return 'paused'
  return caseValue.current_mode === 'search' ? 'active-search' : 'reconstruction'
}

export function caseNumbers(cases: readonly CaseV2[]): Map<string, number> {
  const ordered = [...cases].sort((a, b) => a.created_at.localeCompare(b.created_at) || a.case_id.localeCompare(b.case_id))
  return new Map(ordered.map((caseValue, index) => [caseValue.case_id, index + 1]))
}

export function formatCaseNumber(n: number): string {
  return `#${String(n).padStart(3, '0')}`
}

export function caseMeta(caseValue: CaseV2): string {
  return [
    plural(caseValue.timeline?.events.length ?? 0, 'событие', 'события', 'событий'),
    plural(caseValue.search_checks.length, 'проверка', 'проверки', 'проверок'),
  ].join(' · ')
}

export interface CaseCardView {
  id: string
  title: string
  caseId: string
  status: CaseStatusKey
  place?: string
  updated: string
  counts: string[]
  icon: string
}

export function caseCardView(caseValue: CaseV2, n: number, now: Date = new Date()): CaseCardView {
  const timeline = timelineView(caseValue)
  const progress = searchProgress(caseValue)
  const lastKnown = timeline.items.filter(item => item.status !== 'unknown').pop()
  const counts: string[] = []
  if (progress.total) counts.push(`${progress.done} из ${progress.total} зон`)
  if (caseValue.search_checks.length) counts.push(plural(caseValue.search_checks.length, 'проверка', 'проверки', 'проверок'))
  if (timeline.unknownCount) counts.push(plural(timeline.unknownCount, 'неизвестный интервал', 'неизвестных интервала', 'неизвестных интервалов'))
  return {
    id: caseValue.case_id,
    title: caseValue.item_label,
    caseId: formatCaseNumber(n),
    status: caseStatus(caseValue),
    place: lastKnown?.title,
    updated: formatUpdated(caseValue.updated_at, now),
    counts,
    icon: vocab(itemKind(caseValue)).icon,
  }
}

const FILTERS: Array<[CaseFilter, string, (c: CaseV2) => boolean]> = [
  ['all', 'Все', () => true],
  ['active', 'Активные', c => c.lifecycle === 'active'],
  ['paused', 'Пауза', c => c.lifecycle === 'paused'],
  ['done', 'Завершённые', c => isClosed(c)],
]

export function listFilters(cases: readonly CaseV2[]): Array<{ value: CaseFilter, label: string, count: number }> {
  return FILTERS.map(([value, label, predicate]) => ({ value, label, count: cases.filter(predicate).length }))
}

export function filterCases<T extends CaseV2>(cases: readonly T[], filter: CaseFilter): T[] {
  const predicate = FILTERS.find(([value]) => value === filter)?.[2] ?? (() => true)
  return cases.filter(predicate)
}

export function caseStats(cases: readonly CaseV2[]): Array<{ label: string, n: number }> {
  return [
    { label: 'В поиске', n: cases.filter(c => c.lifecycle === 'active' && c.current_mode === 'search').length },
    { label: 'Восстановление', n: cases.filter(c => c.lifecycle === 'active' && c.current_mode !== 'search').length },
    { label: 'Завершено', n: cases.filter(isClosed).length },
  ]
}

export function sortByUpdated<T extends CaseV2>(cases: readonly T[]): T[] {
  return [...cases].sort((a, b) => b.updated_at.localeCompare(a.updated_at))
}

export interface HomeSummary {
  active: CaseV2 | null
  activeSub: string
  activeIcon: string
  listSub: string
}

export function homeSummary(cases: readonly CaseV2[]): HomeSummary {
  const open = cases.filter(c => !isClosed(c))
  const active = sortByUpdated(open)[0] ?? null
  const activity = !active
    ? ''
    : active.lifecycle === 'paused'
      ? 'приостановлено'
      : active.current_mode === 'search'
        ? (itemKind(active) === 'digital' ? 'проверка источников' : 'физический поиск')
        : 'восстановление'
  return {
    active,
    activeSub: active ? `Продолжить · ${activity}` : '',
    activeIcon: active?.current_mode === 'search' ? 'search' : 'waypoints',
    listSub: `${plural(cases.length, 'дело', 'дела', 'дел')} · ${open.length} открыто`,
  }
}
