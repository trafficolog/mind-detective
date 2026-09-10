export type EvalEventName =
  | 'case_started'
  | 'next_action_shown'
  | 'next_action_started'
  | 'next_action_rejected'
  | 'check_started'
  | 'check_finished'
  | 'duplicate_check_detected'
  | 'check_quality_clarified'
  | 'ai_guard_blocked'
  | 'assistant_offline_fallback'
  | 'local_execution_failed'
  | 'pending_command_started'
  | 'pending_command_retried'
  | 'pending_command_failed'
  | 'pause'
  | 'resume'
  | 'found'
  | 'case_closed_unresolved'
  | 'case_abandoned'
  | 'found_context_recorded'

export interface EvalEvent {
  event_id: string
  event: EvalEventName
  at: string
  metadata: Record<string, string | number | boolean | null>
}

const DB_NAME = 'mind-detective-evaluation'
const DB_VERSION = 1
const STORE = 'events'

const ALLOWED_KEYS = new Set([
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

const SENSITIVE_KEYS = new Set([
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

export class EvalLogError extends Error {
  constructor(public readonly code: string, message: string) {
    super(message)
  }
}

function validateMetadata(metadata: Record<string, unknown>): Record<string, string | number | boolean | null> {
  const safe: Record<string, string | number | boolean | null> = {}
  for (const [key, value] of Object.entries(metadata)) {
    if (SENSITIVE_KEYS.has(key)) {
      throw new EvalLogError('MD_WEB_EVAL_SENSITIVE_FIELD', `sensitive evaluation field: ${key}`)
    }
    if (!ALLOWED_KEYS.has(key)) {
      throw new EvalLogError('MD_WEB_EVAL_FIELD', `unexpected evaluation field: ${key}`)
    }
    if (value !== null && !['string', 'number', 'boolean'].includes(typeof value)) {
      throw new EvalLogError('MD_WEB_EVAL_VALUE', `invalid evaluation value: ${key}`)
    }
    safe[key] = value as string | number | boolean | null
  }
  return safe
}

function openDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === 'undefined') return Promise.reject(new Error('MD_WEB_EVAL_IDB_UNAVAILABLE'))
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    request.onupgradeneeded = () => {
      if (!request.result.objectStoreNames.contains(STORE)) {
        request.result.createObjectStore(STORE, { keyPath: 'event_id' })
      }
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error ?? new Error('MD_WEB_EVAL_IDB_OPEN'))
  })
}

async function persist(event: EvalEvent): Promise<void> {
  const database = await openDatabase()
  try {
    await new Promise<void>((resolve, reject) => {
      const transaction = database.transaction(STORE, 'readwrite')
      transaction.objectStore(STORE).put(structuredClone(event))
      transaction.oncomplete = () => resolve()
      transaction.onerror = () => reject(transaction.error ?? new Error('MD_WEB_EVAL_IDB_WRITE'))
      transaction.onabort = () => reject(transaction.error ?? new Error('MD_WEB_EVAL_IDB_ABORT'))
    })
  } finally {
    database.close()
  }
}

export function appendEvalEvent(event: EvalEventName, metadata: Record<string, unknown> = {}): Promise<void> {
  const safeMetadata = validateMetadata(metadata)
  const record: EvalEvent = {
    event_id: crypto.randomUUID(),
    event,
    at: new Date().toISOString(),
    metadata: safeMetadata,
  }
  return persist(record)
}

export async function listEvalEvents(): Promise<EvalEvent[]> {
  const database = await openDatabase()
  try {
    return await new Promise<EvalEvent[]>((resolve, reject) => {
      const transaction = database.transaction(STORE, 'readonly')
      const request = transaction.objectStore(STORE).getAll()
      request.onsuccess = () => resolve((request.result as EvalEvent[]).sort((a, b) => a.at.localeCompare(b.at)))
      request.onerror = () => reject(request.error ?? new Error('MD_WEB_EVAL_IDB_READ'))
    })
  } finally {
    database.close()
  }
}

export function exportEvalJson(events: readonly EvalEvent[]): Blob {
  return new Blob([JSON.stringify(events, null, 2)], { type: 'application/json' })
}

function csvCell(value: unknown): string {
  const text = typeof value === 'string' ? value : JSON.stringify(value)
  return `"${text.replaceAll('"', '""')}"`
}

export function exportEvalCsv(events: readonly EvalEvent[]): Blob {
  const rows = ['event_id,event,at,metadata']
  for (const event of events) {
    rows.push([event.event_id, event.event, event.at, event.metadata].map(csvCell).join(','))
  }
  return new Blob([`${rows.join('\n')}\n`], { type: 'text/csv;charset=utf-8' })
}
