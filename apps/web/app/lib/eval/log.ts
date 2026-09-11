import {
  type EvalEventName,
  type EvaluationExportV1,
  type EvaluationPrimitive,
  EvalLogError,
  validateEventMetadata,
} from './contracts'
import {
  appendEvaluationEvent,
  appendLegacyEvaluationEvent,
  buildEvaluationExport,
  listEvaluationEvents,
} from './store'

export type { EvalEventName, EvaluationExportV1 } from './contracts'
export { EvalLogError } from './contracts'

/**
 * Legacy pre-v1 event shape. Rows written through this shape have no
 * evaluation_session_id and are intentionally excluded from v1 exports.
 */
export interface EvalEvent {
  event_id: string
  event: EvalEventName
  at: string
  metadata: Record<string, EvaluationPrimitive>
}

const LEGACY_ALLOWED_KEYS = new Set([
  'case_id',
  'arm',
  'mode',
  'outcome_code',
  'duration_bucket',
  'reason_code',
  'command_id',
  'persistence_state',
  'found_context',
  'guard_code',
  'candidate_id',
])

const LEGACY_SENSITIVE_KEYS = new Set([
  'case',
  'item_label',
  'location',
  'target',
  'journal',
  'journal_text',
  'statement',
  'statement_text',
  'user_text',
  'model_text',
  'raw_model_output',
])

function validateLegacyMetadata(metadata: Record<string, unknown>): Record<string, EvaluationPrimitive> {
  const safe: Record<string, EvaluationPrimitive> = {}
  for (const [key, value] of Object.entries(metadata)) {
    if (LEGACY_SENSITIVE_KEYS.has(key)) {
      throw new EvalLogError('MD_WEB_EVAL_SENSITIVE_FIELD', `sensitive evaluation field: ${key}`)
    }
    if (!LEGACY_ALLOWED_KEYS.has(key)) {
      throw new EvalLogError('MD_WEB_EVAL_FIELD', `unexpected evaluation field: ${key}`)
    }
    if (value !== null && !['string', 'number', 'boolean'].includes(typeof value)) {
      throw new EvalLogError('MD_WEB_EVAL_VALUE', `invalid evaluation value: ${key}`)
    }
    if (typeof value === 'string' && value.length > 256) {
      throw new EvalLogError('MD_WEB_EVAL_VALUE', `evaluation string too long: ${key}`)
    }
    if (typeof value === 'number' && !Number.isFinite(value)) {
      throw new EvalLogError('MD_WEB_EVAL_VALUE', `invalid evaluation number: ${key}`)
    }
    safe[key] = value as EvaluationPrimitive
  }
  return safe
}

export function appendEvalEvent(
  evaluationSessionId: string,
  event: EvalEventName,
  metadata?: Record<string, unknown>,
): Promise<void>
/** @deprecated Ordinary unbound logging is retained only until evaluation instrumentation is migrated. */
export function appendEvalEvent(event: EvalEventName, metadata?: Record<string, unknown>): Promise<void>
export function appendEvalEvent(
  first: string,
  second: EvalEventName | Record<string, unknown> = {},
  third: Record<string, unknown> = {},
): Promise<void> {
  if (typeof second === 'string') {
    const metadata = validateEventMetadata(second, third)
    return appendEvaluationEvent(first, second, metadata).then(() => undefined)
  }

  const event = first as EvalEventName
  const safeMetadata = validateLegacyMetadata(second)
  const record: EvalEvent = {
    event_id: crypto.randomUUID(),
    event,
    at: new Date().toISOString(),
    metadata: safeMetadata,
  }
  return appendLegacyEvaluationEvent(record)
}

export async function listEvalEvents(): Promise<ReturnType<typeof listEvaluationEvents> extends Promise<infer T> ? T : never> {
  return await listEvaluationEvents()
}

export { buildEvaluationExport }

export function exportEvalJson(bundle: EvaluationExportV1 | readonly EvalEvent[]): Blob {
  return new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
}

function csvCell(value: unknown): string {
  const text = typeof value === 'string' ? value : JSON.stringify(value)
  return `"${text.replaceAll('"', '""')}"`
}

function exportBundleCsv(bundle: EvaluationExportV1): Blob {
  const rows = ['record_type,record_id,evaluation_session_id,at,payload']
  for (const participant of bundle.participants) {
    rows.push([
      'participant',
      participant.participant_id,
      '',
      participant.created_at,
      participant,
    ].map(csvCell).join(','))
  }
  for (const session of bundle.sessions) {
    rows.push([
      'session',
      session.evaluation_session_id,
      session.evaluation_session_id,
      session.started_at ?? '',
      session,
    ].map(csvCell).join(','))
  }
  for (const event of bundle.events) {
    rows.push([
      'event',
      event.event_id,
      event.evaluation_session_id,
      event.at,
      { event: event.event, metadata: event.metadata },
    ].map(csvCell).join(','))
  }
  return new Blob([`${rows.join('\n')}\n`], { type: 'text/csv;charset=utf-8' })
}

export function exportEvalCsv(bundle: EvaluationExportV1 | readonly EvalEvent[]): Blob {
  if (!Array.isArray(bundle)) return exportBundleCsv(bundle as EvaluationExportV1)

  const rows = ['event_id,event,at,metadata']
  for (const event of bundle) {
    rows.push([event.event_id, event.event, event.at, event.metadata].map(csvCell).join(','))
  }
  return new Blob([`${rows.join('\n')}\n`], { type: 'text/csv;charset=utf-8' })
}
