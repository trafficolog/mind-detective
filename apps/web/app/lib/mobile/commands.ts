// Typed input from the mobile screens → portable command envelopes.
// Validation here only guards input shape (UX); Case semantics stay in the generated kernel.
import type { CaseV2, CommandEnvelope } from '../api/contracts'
import { parseClock } from './timeMask'
import { findCandidateId, hasFreeAccount } from './viewModel'
import { PRECISIONS, RESULTS, STATEMENT_TYPES, vocab, type ItemKind, type PrecisionKey, type ResultKey } from './vocab'

export class MobileInputError extends Error {
  constructor(public readonly code: string) {
    super(code)
    this.name = 'MobileInputError'
  }
}

export interface EnvelopeContext {
  now?: string
  id?: string
}

function need(condition: unknown, code: string): void {
  if (!condition) throw new MobileInputError(code)
}

function newId(): string {
  return globalThis.crypto.randomUUID()
}

export function envelope(
  caseValue: CaseV2,
  commandType: CommandEnvelope['command_type'],
  payload: Record<string, unknown>,
  ctx: EnvelopeContext = {},
): CommandEnvelope {
  return {
    command_id: ctx.id ?? newId(),
    expected_updated_at: caseValue.updated_at,
    command_type: commandType,
    now: ctx.now ?? new Date().toISOString(),
    payload,
  }
}

export function setModeCommand(caseValue: CaseV2, mode: 'reconstruction' | 'search', ctx: EnvelopeContext = {}): CommandEnvelope {
  return envelope(caseValue, 'set_mode', { mode }, ctx)
}

/** I1: text is sent verbatim; the first account is recorded, later edits are append-only revisions. */
export function freeAccountCommand(caseValue: CaseV2, text: string, ctx: EnvelopeContext = {}): CommandEnvelope {
  need(String(text ?? '').trim(), 'text_required')
  const id = ctx.id ?? newId()
  return hasFreeAccount(caseValue)
    ? envelope(caseValue, 'revise_free_account', { entry_id: `free-account-${id}`, text }, { ...ctx, id })
    : envelope(caseValue, 'record_free_account', { entry_id: `free-account-${id}`, text }, { ...ctx, id })
}

export interface StatementInput {
  type: string
  text: string
  time?: string
  limitation?: string
}

export function statementCommand(caseValue: CaseV2, input: StatementInput, ctx: EnvelopeContext = {}): CommandEnvelope {
  need(input.type in STATEMENT_TYPES, 'type_invalid')
  const text = String(input.text ?? '').trim()
  need(text, 'text_required')
  const rawTime = String(input.time ?? '').trim()
  const time = rawTime ? parseClock(rawTime) : null
  need(!rawTime || time, 'time_invalid')
  const limitation = String(input.limitation ?? '').trim()
  const id = ctx.id ?? newId()
  return envelope(caseValue, 'add_statement', {
    statement_id: `statement-${id}`,
    source: 'user',
    statement_type: input.type,
    original_text: text,
    event_time: time,
    user_confirmation: true,
    supporting_evidence_ids: [],
    limitations: limitation ? [limitation] : [],
  }, { ...ctx, id })
}

export interface EventInput {
  title: string
  precision: string
  time?: string
}

export function eventCommand(caseValue: CaseV2, input: EventInput, ctx: EnvelopeContext = {}): CommandEnvelope {
  const title = String(input.title ?? '').trim()
  need(title, 'title_required')
  need(input.precision in PRECISIONS, 'precision_invalid')
  const precision = input.precision as PrecisionKey
  const time = precision === 'unknown' ? null : parseClock(String(input.time ?? ''))
  need(precision === 'unknown' || time, 'time_invalid')
  const id = ctx.id ?? newId()
  const timeline = caseValue.timeline
  return envelope(caseValue, 'rebuild_timeline', {
    events: [
      ...(timeline?.events ?? []).map(event => ({ ...event, statement_ids: [...event.statement_ids] })),
      { id: `event-${id}`, label: title, statement_ids: [], event_time: time, time_precision: precision },
    ],
    last_supported_interaction_id: timeline?.last_supported_interaction_id ?? null,
    first_noticed_missing_id: timeline?.first_noticed_missing_id ?? null,
  }, { ...ctx, id })
}

export function targetCommand(caseValue: CaseV2, name: string, ctx: EnvelopeContext = {}): CommandEnvelope {
  const target = String(name ?? '').trim()
  need(target, 'title_required')
  const id = ctx.id ?? newId()
  return envelope(caseValue, 'add_search_target', { statement_id: `target-${id}`, target }, { ...ctx, id })
}

export interface CheckInput {
  place: string
  method: string
  result: string
  note?: string
}

export function checkCommand(caseValue: CaseV2, input: CheckInput, ctx: EnvelopeContext = {}): CommandEnvelope {
  const place = String(input.place ?? '').trim()
  need(place, 'place_required')
  need(input.result in RESULTS, 'result_invalid')
  const note = String(input.note ?? '').trim()
  const candidateId = findCandidateId(caseValue, place)
  const id = ctx.id ?? newId()
  return envelope(caseValue, 'record_search_check', {
    check_id: `check-${id}`,
    target: place,
    method: input.method,
    result: input.result as ResultKey,
    based_on: candidateId ? [candidateId] : [],
    notes: note ? [note] : [],
  }, { ...ctx, id })
}

const FOUND_CONTEXT: Record<string, string> = {
  current: 'current_suggested_action',
  elsewhere: 'elsewhere_unplanned',
  previous: 'after_previous_check',
  unknown: 'unknown',
}

export function closeCommand(caseValue: CaseV2, outcome: 'found' | 'closed', where: string, ctx: EnvelopeContext = {}): CommandEnvelope {
  if (outcome === 'found') {
    return envelope(caseValue, 'close_found', { outcome: { found_context: FOUND_CONTEXT[where] ?? 'unknown' } }, ctx)
  }
  return envelope(caseValue, 'close_unresolved', { outcome: {} }, ctx)
}

/** T15: a check with result «Нашёл» is followed by an explicit close_found on the updated case. */
export function afterCheckCommand(updated: CaseV2, result: string, ctx: EnvelopeContext = {}): CommandEnvelope | null {
  return result === 'found' ? closeCommand(updated, 'found', 'current', ctx) : null
}

export function pauseToggleCommand(caseValue: CaseV2, ctx: EnvelopeContext = {}): CommandEnvelope {
  return envelope(caseValue, caseValue.lifecycle === 'paused' ? 'resume' : 'pause', {}, ctx)
}

const MESSAGES: Record<string, string> = {
  title_required: 'Введите название.',
  text_required: 'Введите текст.',
  type_invalid: 'Выберите тип сведения.',
  precision_invalid: 'Выберите точность времени.',
  time_invalid: 'Укажите время в формате ЧЧ:ММ.',
  place_required: 'Укажите место.',
  result_invalid: 'Выберите результат проверки.',
  import_invalid: 'Не удалось импортировать дело: файл или версия схемы не поддерживается.',
  MD_CASE_TERMINAL: 'Дело завершено и не изменяется.',
  MD_CASE_STATE: 'Дело на паузе. Продолжите его в меню дела.',
  MD_RECON_FREE_ACCOUNT_REQUIRED: 'Сначала сохраните свободный рассказ.',
  MD_RECON_EVENT_TIME_INVALID: 'Укажите время в формате ЧЧ:ММ.',
  MD_RECON_MODE_REQUIRED: 'Сначала выберите, с чего начать.',
  MD_WEB_STALE_COMMAND: 'Дело изменилось в другой вкладке. Откройте его заново.',
  MD_WEB_COMMAND_PAYLOAD: 'Проверьте введённые данные.',
  server_unavailable: 'Сервер ассистента недоступен.',
  server_config_invalid: 'Адрес сервера не подходит: нужен https или localhost.',
  stt_empty: 'Речь не распознана. Попробуйте ещё раз.',
  stt_unavailable: 'Сервис распознавания недоступен. Проверьте адрес, ключ и CORS.',
  stt_config_invalid: 'Адрес распознавания не подходит: нужен https или localhost.',
  MD_SAFE: 'Этот запрос касается потенциально опасного действия, поэтому Mind Detective не использует поиск вещей для ответа. Проверьте факт надёжным и безопасным способом или обратитесь за подходящей помощью.',
}

export function errorMessage(code: string, kind: ItemKind): string {
  if (code === 'MD_SEARCH_TARGET_EXISTS') return vocab(kind).exists
  if (code === 'MD_SEARCH_MODE_REQUIRED') return vocab(kind).notInSearch
  if (code.startsWith('MD_SAFE_')) return MESSAGES.MD_SAFE!
  return MESSAGES[code] ?? 'Не удалось сохранить.'
}

export function errorCodeOf(error: unknown): string {
  if (error && typeof error === 'object' && 'code' in error && typeof (error as { code: unknown }).code === 'string') {
    return (error as { code: string }).code
  }
  return error instanceof Error ? error.message : 'unknown'
}
