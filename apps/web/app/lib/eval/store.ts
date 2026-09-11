import {
  EVALUATION_EXPORT_SCHEMA,
  EVALUATION_SCHEMA,
  type EvalEventName,
  type EvaluationEventV1,
  type EvaluationExportV1,
  type EvaluationOutcome,
  type EvaluationParticipantV1,
  type EvaluationSessionV1,
  validateEvaluationParticipant,
  validateEvaluationSession,
  validateEventMetadata,
} from './contracts'

const DB_NAME = 'mind-detective-evaluation'
export const EVALUATION_DB_VERSION = 2
const PARTICIPANTS = 'participants'
const SESSIONS = 'sessions'
const EVENTS = 'events'
const SESSION_CASE_INDEX = 'case_id'
const EVENT_SESSION_INDEX = 'evaluation_session_id'

interface LegacyEvalEventRecord {
  event_id: string
  event: string
  at: string
  metadata: Record<string, unknown>
  evaluation_session_id?: string
}

const POST_SESSION_EVENTS = new Set<EvalEventName>([
  'post_case_rating',
  'proposal_safety_annotation',
  'handoff_rubric',
])

function requestResult<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error ?? new Error('MD_WEB_EVAL_IDB_REQUEST'))
  })
}

function transactionDone(transaction: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve()
    transaction.onerror = () => reject(transaction.error ?? new Error('MD_WEB_EVAL_IDB_TRANSACTION'))
    transaction.onabort = () => reject(transaction.error ?? new Error('MD_WEB_EVAL_IDB_ABORT'))
  })
}

function sorted<T>(items: T[], key: (item: T) => string): T[] {
  return items.sort((left, right) => key(left).localeCompare(key(right)))
}

export function openEvaluationDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === 'undefined') return Promise.reject(new Error('MD_WEB_EVAL_IDB_UNAVAILABLE'))

  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, EVALUATION_DB_VERSION)
    request.onupgradeneeded = () => {
      const database = request.result
      if (!database.objectStoreNames.contains(PARTICIPANTS)) {
        database.createObjectStore(PARTICIPANTS, { keyPath: 'participant_id' })
      }
      if (!database.objectStoreNames.contains(SESSIONS)) {
        const sessions = database.createObjectStore(SESSIONS, { keyPath: 'evaluation_session_id' })
        sessions.createIndex(SESSION_CASE_INDEX, 'case_id', { unique: true })
      } else {
        const sessions = request.transaction?.objectStore(SESSIONS)
        if (sessions && !sessions.indexNames.contains(SESSION_CASE_INDEX)) {
          sessions.createIndex(SESSION_CASE_INDEX, 'case_id', { unique: true })
        }
      }
      if (!database.objectStoreNames.contains(EVENTS)) {
        const events = database.createObjectStore(EVENTS, { keyPath: 'event_id' })
        events.createIndex(EVENT_SESSION_INDEX, 'evaluation_session_id', { unique: false })
      } else {
        const events = request.transaction?.objectStore(EVENTS)
        if (events && !events.indexNames.contains(EVENT_SESSION_INDEX)) {
          events.createIndex(EVENT_SESSION_INDEX, 'evaluation_session_id', { unique: false })
        }
      }
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error ?? new Error('MD_WEB_EVAL_IDB_OPEN'))
    request.onblocked = () => reject(new Error('MD_WEB_EVAL_IDB_BLOCKED'))
  })
}

async function withDatabase<T>(run: (database: IDBDatabase) => Promise<T>): Promise<T> {
  const database = await openEvaluationDatabase()
  try {
    return await run(database)
  } finally {
    database.close()
  }
}

export function sessionAssignmentMatches(left: EvaluationSessionV1, right: EvaluationSessionV1): boolean {
  return left.evaluation_session_id === right.evaluation_session_id
    && left.participant_id === right.participant_id
    && left.protocol === right.protocol
    && left.arm === right.arm
    && left.assignment_version === right.assignment_version
    && left.counterbalance_cell === right.counterbalance_cell
    && left.scenario_family === right.scenario_family
    && left.scenario_variant === right.scenario_variant
    && left.order_position === right.order_position
}

export function filterExportableEvents(
  sessions: readonly EvaluationSessionV1[],
  events: readonly LegacyEvalEventRecord[],
): EvaluationEventV1[] {
  const sessionIds = new Set(sessions.map(session => session.evaluation_session_id))
  const exportable: EvaluationEventV1[] = []

  for (const event of events) {
    if (!event.evaluation_session_id || !sessionIds.has(event.evaluation_session_id)) continue
    if (!event.event_id || !event.at) continue
    const eventName = event.event as EvalEventName
    const metadata = validateEventMetadata(eventName, event.metadata)
    exportable.push({
      event_id: event.event_id,
      evaluation_session_id: event.evaluation_session_id,
      event: eventName,
      at: event.at,
      metadata,
    })
  }

  return sorted(exportable, event => `${event.at}\u0000${event.event_id}`)
}

export function validateEvaluationEventForSession(
  session: EvaluationSessionV1,
  event: EvalEventName,
  metadata: Record<string, unknown>,
  existingEvents: readonly EvaluationEventV1[],
): void {
  const safe = validateEventMetadata(event, metadata)
  const sessionEnded = session.outcome !== null || session.ended_at !== null
  if (sessionEnded && !POST_SESSION_EVENTS.has(event)) {
    throw new Error('MD_WEB_EVAL_SESSION_ENDED')
  }

  const existing = existingEvents.filter(value => value.evaluation_session_id === session.evaluation_session_id)

  if (event === 'post_case_rating') {
    if (!sessionEnded || session.outcome === null || session.ended_at === null) {
      throw new Error('MD_WEB_EVAL_RATING_BEFORE_END')
    }
    if (existing.some(value => value.event === 'post_case_rating')) {
      throw new Error('MD_WEB_EVAL_RATING_EXISTS')
    }
    return
  }

  if (event === 'proposal_safety_annotation') {
    if (session.protocol !== 'staged') {
      throw new Error('MD_WEB_EVAL_OBSERVER_STAGED_ONLY')
    }
    const proposalId = safe.proposal_id
    if (typeof proposalId !== 'string' || !existing.some(value =>
      value.event === 'next_action_shown' && value.metadata.proposal_id === proposalId,
    )) {
      throw new Error('MD_WEB_EVAL_PROPOSAL_UNKNOWN')
    }
    if (existing.some(value =>
      value.event === 'proposal_safety_annotation' && value.metadata.proposal_id === proposalId,
    )) {
      throw new Error('MD_WEB_EVAL_PROPOSAL_ANNOTATED')
    }
    return
  }

  if (event === 'handoff_rubric') {
    if (session.protocol !== 'staged') {
      throw new Error('MD_WEB_EVAL_OBSERVER_STAGED_ONLY')
    }
    if (session.scenario_family !== 'S4') {
      throw new Error('MD_WEB_EVAL_HANDOFF_S4_ONLY')
    }
    if (existing.some(value => value.event === 'handoff_rubric')) {
      throw new Error('MD_WEB_EVAL_HANDOFF_EXISTS')
    }
    const score = [
      safe.mode_restored,
      safe.prior_checks_preserved,
      safe.journal_continuity,
      safe.next_action_coherent,
    ].filter(value => value === true).length
    if (safe.handoff_score !== score) {
      throw new Error('MD_WEB_EVAL_HANDOFF_SCORE_MISMATCH')
    }
  }
}

export async function createEvaluationParticipant(participant: EvaluationParticipantV1): Promise<EvaluationParticipantV1> {
  validateEvaluationParticipant(participant)
  return await withDatabase(async (database) => {
    const transaction = database.transaction(PARTICIPANTS, 'readwrite')
    const done = transactionDone(transaction)
    try {
      transaction.objectStore(PARTICIPANTS).add(structuredClone(participant))
      await done
      return participant
    } catch (error) {
      try { transaction.abort() } catch { /* transaction may already be closed */ }
      try { await done } catch { /* expected on abort */ }
      throw error instanceof DOMException && error.name === 'ConstraintError'
        ? new Error('MD_WEB_EVAL_PARTICIPANT_EXISTS')
        : error
    }
  })
}

export async function createEvaluationSession(session: EvaluationSessionV1): Promise<EvaluationSessionV1> {
  validateEvaluationSession(session)
  return await withDatabase(async (database) => {
    const transaction = database.transaction(SESSIONS, 'readwrite')
    const done = transactionDone(transaction)
    const store = transaction.objectStore(SESSIONS)
    const existing = await requestResult(store.get(session.evaluation_session_id)) as EvaluationSessionV1 | undefined
    if (existing !== undefined) {
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      if (!sessionAssignmentMatches(existing, session)) throw new Error('MD_WEB_EVAL_ASSIGNMENT_IMMUTABLE')
      throw new Error('MD_WEB_EVAL_SESSION_EXISTS')
    }
    store.add(structuredClone(session))
    await done
    return session
  })
}

export async function getEvaluationSession(sessionId: string): Promise<EvaluationSessionV1 | null> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction(SESSIONS, 'readonly')
    const done = transactionDone(transaction)
    const value = await requestResult(transaction.objectStore(SESSIONS).get(sessionId))
    await done
    return (value as EvaluationSessionV1 | undefined) ?? null
  })
}

export async function getEvaluationSessionByCaseId(caseId: string): Promise<EvaluationSessionV1 | null> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction(SESSIONS, 'readonly')
    const done = transactionDone(transaction)
    const value = await requestResult(transaction.objectStore(SESSIONS).index(SESSION_CASE_INDEX).get(caseId))
    await done
    return (value as EvaluationSessionV1 | undefined) ?? null
  })
}

export async function listEvaluationParticipants(): Promise<EvaluationParticipantV1[]> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction(PARTICIPANTS, 'readonly')
    const done = transactionDone(transaction)
    const values = await requestResult(transaction.objectStore(PARTICIPANTS).getAll()) as EvaluationParticipantV1[]
    await done
    return sorted(values, value => value.created_at)
  })
}

export async function listEvaluationSessions(): Promise<EvaluationSessionV1[]> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction(SESSIONS, 'readonly')
    const done = transactionDone(transaction)
    const values = await requestResult(transaction.objectStore(SESSIONS).getAll()) as EvaluationSessionV1[]
    await done
    return sorted(values, value => `${value.participant_id}\u0000${value.order_position ?? 0}\u0000${value.evaluation_session_id}`)
  })
}

export async function listEvaluationEvents(sessionId?: string): Promise<EvaluationEventV1[]> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction([SESSIONS, EVENTS], 'readonly')
    const done = transactionDone(transaction)
    const sessions = await requestResult(transaction.objectStore(SESSIONS).getAll()) as EvaluationSessionV1[]
    const eventStore = transaction.objectStore(EVENTS)
    let raw: LegacyEvalEventRecord[]
    if (sessionId) {
      raw = await requestResult(eventStore.index(EVENT_SESSION_INDEX).getAll(sessionId)) as LegacyEvalEventRecord[]
    } else {
      raw = await requestResult(eventStore.getAll()) as LegacyEvalEventRecord[]
    }
    await done
    return filterExportableEvents(sessions, raw)
  })
}

function eventRecord(
  sessionId: string,
  event: EvalEventName,
  metadata: Record<string, unknown>,
  at: string,
): EvaluationEventV1 {
  return {
    event_id: crypto.randomUUID(),
    evaluation_session_id: sessionId,
    event,
    at,
    metadata: validateEventMetadata(event, metadata),
  }
}

export async function appendEvaluationEvent(
  sessionId: string,
  event: EvalEventName,
  metadata: Record<string, unknown> = {},
  at = new Date().toISOString(),
): Promise<EvaluationEventV1> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction([SESSIONS, EVENTS], 'readwrite')
    const done = transactionDone(transaction)
    const session = await requestResult(transaction.objectStore(SESSIONS).get(sessionId)) as EvaluationSessionV1 | undefined
    if (!session) {
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw new Error('MD_WEB_EVAL_SESSION_NOT_FOUND')
    }

    const eventStore = transaction.objectStore(EVENTS)
    const existingRaw = await requestResult(eventStore.index(EVENT_SESSION_INDEX).getAll(sessionId)) as LegacyEvalEventRecord[]
    const existing = filterExportableEvents([session], existingRaw)
    try {
      validateEvaluationEventForSession(session, event, metadata, existing)
    } catch (error) {
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw error
    }

    const record = eventRecord(sessionId, event, metadata, at)
    eventStore.add(structuredClone(record))
    await done
    return record
  })
}

export async function appendLegacyEvaluationEvent(record: LegacyEvalEventRecord): Promise<void> {
  await withDatabase(async (database) => {
    const transaction = database.transaction(EVENTS, 'readwrite')
    const done = transactionDone(transaction)
    transaction.objectStore(EVENTS).add(structuredClone(record))
    await done
  })
}

export async function startEvaluationSessionCase(
  sessionId: string,
  caseId: string,
  startedAt: string,
): Promise<EvaluationSessionV1> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction([SESSIONS, EVENTS], 'readwrite')
    const done = transactionDone(transaction)
    const sessions = transaction.objectStore(SESSIONS)
    const session = await requestResult(sessions.get(sessionId)) as EvaluationSessionV1 | undefined
    if (!session) {
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw new Error('MD_WEB_EVAL_SESSION_NOT_FOUND')
    }
    if (session.protocol === 'external_a') {
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw new Error('MD_WEB_EVAL_EXTERNAL_ARM')
    }
    if (session.case_id !== null || session.started_at !== null) {
      if (session.case_id === caseId && session.started_at === startedAt) {
        await done
        return session
      }
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw new Error('MD_WEB_EVAL_ASSIGNMENT_IMMUTABLE')
    }

    const updated: EvaluationSessionV1 = { ...session, case_id: caseId, started_at: startedAt }
    validateEvaluationSession(updated)
    sessions.put(structuredClone(updated))
    transaction.objectStore(EVENTS).add(structuredClone(eventRecord(sessionId, 'case_started', { case_id: caseId }, startedAt)))
    await done
    return updated
  })
}

function terminalEvent(outcome: EvaluationOutcome): EvalEventName {
  if (outcome === 'found') return 'found'
  if (outcome === 'unresolved') return 'case_closed_unresolved'
  return 'case_abandoned'
}

export async function finishEvaluationSession(
  sessionId: string,
  outcome: EvaluationOutcome,
  endedAt: string,
  terminalMetadata: Record<string, unknown> = {},
): Promise<EvaluationSessionV1> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction([SESSIONS, EVENTS], 'readwrite')
    const done = transactionDone(transaction)
    const sessions = transaction.objectStore(SESSIONS)
    const session = await requestResult(sessions.get(sessionId)) as EvaluationSessionV1 | undefined
    if (!session) {
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw new Error('MD_WEB_EVAL_SESSION_NOT_FOUND')
    }
    if (!session.case_id || !session.started_at) {
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw new Error('MD_WEB_EVAL_SESSION_NOT_STARTED')
    }
    if (session.outcome !== null || session.ended_at !== null) {
      if (session.outcome === outcome) {
        await done
        return session
      }
      transaction.abort()
      try { await done } catch { /* expected abort */ }
      throw new Error('MD_WEB_EVAL_OUTCOME_IMMUTABLE')
    }

    const updated: EvaluationSessionV1 = { ...session, outcome, ended_at: endedAt }
    sessions.put(structuredClone(updated))
    transaction.objectStore(EVENTS).add(structuredClone(eventRecord(
      sessionId,
      terminalEvent(outcome),
      { ...terminalMetadata, case_id: session.case_id },
      endedAt,
    )))
    await done
    return updated
  })
}

export async function buildEvaluationExport(exportedAt = new Date().toISOString()): Promise<EvaluationExportV1> {
  return await withDatabase(async (database) => {
    const transaction = database.transaction([PARTICIPANTS, SESSIONS, EVENTS], 'readonly')
    const done = transactionDone(transaction)
    const participants = await requestResult(transaction.objectStore(PARTICIPANTS).getAll()) as EvaluationParticipantV1[]
    const sessions = await requestResult(transaction.objectStore(SESSIONS).getAll()) as EvaluationSessionV1[]
    const rawEvents = await requestResult(transaction.objectStore(EVENTS).getAll()) as LegacyEvalEventRecord[]
    await done

    const validParticipants = participants
      .filter(value => value.evaluation_schema === EVALUATION_SCHEMA)
      .map(value => validateEvaluationParticipant(value))
    const validSessions = sessions
      .filter(value => value.evaluation_schema === EVALUATION_SCHEMA)
      .map(value => validateEvaluationSession(value))

    return {
      export_schema: EVALUATION_EXPORT_SCHEMA,
      exported_at: exportedAt,
      participants: sorted(validParticipants, value => `${value.created_at}\u0000${value.participant_id}`),
      sessions: sorted(validSessions, value => `${value.participant_id}\u0000${value.order_position ?? 0}\u0000${value.evaluation_session_id}`),
      events: filterExportableEvents(validSessions, rawEvents),
    }
  })
}
