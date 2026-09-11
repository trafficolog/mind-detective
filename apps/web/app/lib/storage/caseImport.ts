import type {
  ActionFeedbackV2,
  CandidateCheckV2,
  CaseLifecycle,
  CaseV2,
  CheckState,
  InteractionMode,
  JournalAuthor,
  JournalEntryV2,
  JournalMode,
  NextActionV2,
  SearchCheckV2,
  SearchMethod,
  SearchResult,
  StatementV2,
  TimelineEventV2,
  TimelineV2,
} from '../api/contracts'

const CASE_SCHEMA_V1 = 'mind-detective-case/v1'
const CASE_SCHEMA_V2 = 'mind-detective-case/v2'

function schemaError(): never {
  throw new Error('MD_WEB_IMPORT_SCHEMA')
}

function asRecord(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) schemaError()
  return value as Record<string, unknown>
}

function asArray(value: unknown): unknown[] {
  if (!Array.isArray(value)) schemaError()
  return value
}

function asString(value: unknown): string {
  if (typeof value !== 'string') schemaError()
  return value
}

function asNullableString(value: unknown): string | null {
  return typeof value === 'string' ? value : null
}

function asStringArray(value: unknown, fallback: string[] | null = null): string[] {
  if (value === undefined && fallback !== null) return [...fallback]
  return asArray(value).map(asString)
}

function asOneOf<T extends string>(value: unknown, allowed: readonly T[]): T {
  const text = asString(value)
  if (!allowed.includes(text as T)) schemaError()
  return text as T
}

function migratePayload(input: Record<string, unknown>): Record<string, unknown> {
  const migrated = structuredClone(input)
  if (migrated.schema === CASE_SCHEMA_V2) return migrated
  if (migrated.schema !== CASE_SCHEMA_V1) schemaError()

  migrated.schema = CASE_SCHEMA_V2
  migrated.current_mode = 'unselected'
  migrated.interaction_journal = []
  migrated.action_feedback = []
  return migrated
}

function statementFromUnknown(value: unknown): StatementV2 {
  const item = asRecord(value)
  return {
    id: asString(item.id),
    source: asOneOf(item.source, ['user', 'file', 'assistant'] as const),
    statement_type: asOneOf(
      item.statement_type,
      ['recollection', 'habit', 'observation', 'hypothesis', 'search_suggestion'] as const,
    ),
    original_text: asString(item.original_text),
    recorded_at: asString(item.recorded_at),
    event_time: asNullableString(item.event_time),
    user_confirmation: Boolean(item.user_confirmation ?? false),
    supporting_evidence_ids: asStringArray(item.supporting_evidence_ids, []),
    limitations: asStringArray(item.limitations, []),
  }
}

function timelineEventFromUnknown(value: unknown): TimelineEventV2 {
  const item = asRecord(value)
  return {
    id: asString(item.id),
    label: asString(item.label),
    statement_ids: asStringArray(item.statement_ids, []),
    event_time: asNullableString(item.event_time),
    time_precision: asString(item.time_precision),
  }
}

function timelineFromUnknown(value: unknown): TimelineV2 | null {
  if (value === null) return null
  const item = asRecord(value)
  return {
    last_supported_interaction_id: asNullableString(item.last_supported_interaction_id),
    first_noticed_missing_id: asNullableString(item.first_noticed_missing_id),
    events: (item.events === undefined ? [] : asArray(item.events)).map(timelineEventFromUnknown),
    unknown_intervals: asStringArray(item.unknown_intervals, []),
    contradictions: asStringArray(item.contradictions, []),
  }
}

function searchCheckFromUnknown(value: unknown): SearchCheckV2 {
  const item = asRecord(value)
  return {
    id: asString(item.id),
    target: asString(item.target),
    method: asOneOf<SearchMethod>(
      item.method,
      ['reported_check', 'glance', 'visual_systematic', 'empty_and_check', 'tactile', 'inaccessible'],
    ),
    started_at: asString(item.started_at),
    completed_at: asNullableString(item.completed_at),
    result: asOneOf<SearchResult>(item.result, ['found', 'not_found', 'partial', 'inaccessible']),
    inaccessible_parts: asStringArray(item.inaccessible_parts, []),
    based_on: asStringArray(item.based_on, []),
    notes: asStringArray(item.notes, []),
  }
}

function candidateFromUnknown(value: unknown): CandidateCheckV2 {
  const item = asRecord(value)
  return {
    id: asString(item.id),
    target: asString(item.target),
    route_relation: asOneOf(item.route_relation, ['direct', 'indirect', 'none'] as const),
    check_state: asOneOf<CheckState>(item.check_state, ['unchecked', 'partial', 'checked']),
    effort: asOneOf(item.effort, ['low', 'medium', 'high'] as const),
    safety: asOneOf(item.safety, ['safe', 'caution', 'unsafe'] as const),
    urgency_relevance: asOneOf(item.urgency_relevance, ['high', 'normal'] as const),
    basis: asOneOf(item.basis, ['episode', 'habit', 'generic'] as const),
    based_on: asStringArray(item.based_on, []),
    rationale: asStringArray(item.rationale, []),
  }
}

function nextActionFromUnknown(value: unknown): NextActionV2 | null {
  if (value === null) return null
  const item = asRecord(value)
  return {
    candidate_id: asString(item.candidate_id),
    target: asString(item.target),
    rationale_codes: asStringArray(item.rationale_codes, []),
  }
}

function journalEntryFromUnknown(value: unknown): JournalEntryV2 {
  const item = asRecord(value)
  return {
    id: asString(item.id),
    author: asOneOf<JournalAuthor>(item.author, ['user', 'assistant', 'system']),
    mode: asOneOf<JournalMode>(item.mode, ['reconstruction', 'search', 'system']),
    entry_type: asString(item.entry_type),
    text: asString(item.text),
    created_at: asString(item.created_at),
    statement_ids: asStringArray(item.statement_ids, []),
    search_check_ids: asStringArray(item.search_check_ids, []),
  }
}

function feedbackFromUnknown(value: unknown): ActionFeedbackV2 {
  const item = asRecord(value)
  return {
    id: asString(item.id),
    candidate_id: asString(item.candidate_id),
    reason: asOneOf(
      item.reason,
      ['already_checked', 'impossible_now', 'irrelevant', 'unsafe_or_uncomfortable', 'other'] as const,
    ),
    recorded_at: asString(item.recorded_at),
  }
}

function outcomeFromUnknown(value: unknown): Record<string, unknown> | null {
  if (value === null) return null
  return structuredClone(asRecord(value))
}

export function migrateAndValidateImportedCase(input: Record<string, unknown>): CaseV2 {
  const item = migratePayload(input)

  return {
    schema: CASE_SCHEMA_V2,
    case_id: asString(item.case_id),
    item_label: asString(item.item_label),
    created_at: asString(item.created_at),
    updated_at: asString(item.updated_at),
    lifecycle: asOneOf<CaseLifecycle>(
      item.lifecycle,
      ['active', 'paused', 'closed_found', 'closed_unresolved', 'deleted'],
    ),
    statements: asArray(item.statements).map(statementFromUnknown),
    timeline: timelineFromUnknown(item.timeline),
    search_checks: asArray(item.search_checks).map(searchCheckFromUnknown),
    candidates: asArray(item.candidates).map(candidateFromUnknown),
    next_action: nextActionFromUnknown(item.next_action),
    constraints: asStringArray(item.constraints),
    outcome: outcomeFromUnknown(item.outcome),
    current_mode: asOneOf<InteractionMode>(item.current_mode, ['unselected', 'reconstruction', 'search']),
    interaction_journal: asArray(item.interaction_journal).map(journalEntryFromUnknown),
    action_feedback: asArray(item.action_feedback).map(feedbackFromUnknown),
  }
}
