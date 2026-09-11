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
  | 'post_case_rating'
  | 'proposal_safety_annotation'
  | 'handoff_rubric'

export type EvaluationProtocol = 'staged' | 'real' | 'external_a'
export type EvaluationArm = 'A' | 'B' | 'C'
export type EvaluationOutcome = 'found' | 'unresolved' | 'abandoned'
export type ScenarioFamily = 'S1' | 'S2' | 'S3' | 'S4'
export type ScenarioVariant = 'A' | 'B'
export type CounterbalanceCell = 1 | 2 | 3 | 4
export type EvaluationPrimitive = string | number | boolean | null

export const EVALUATION_SCHEMA = 'mind-detective-evaluation/v1' as const
export const EVALUATION_EXPORT_SCHEMA = 'mind-detective-evaluation-export/v1' as const
export const EVALUATION_ASSIGNMENT_VERSION = 'eval-assignment/v1' as const

export interface EvaluationParticipantV1 {
  evaluation_schema: typeof EVALUATION_SCHEMA
  participant_id: string
  protocol: EvaluationProtocol
  enrollment_slot: number | null
  counterbalance_cell: CounterbalanceCell | null
  created_at: string
}

export interface EvaluationSessionV1 {
  evaluation_schema: typeof EVALUATION_SCHEMA
  evaluation_session_id: string
  participant_id: string
  protocol: EvaluationProtocol
  arm: EvaluationArm
  assignment_version: typeof EVALUATION_ASSIGNMENT_VERSION
  counterbalance_cell: CounterbalanceCell | null
  scenario_family: ScenarioFamily | null
  scenario_variant: ScenarioVariant | null
  order_position: 1 | 2 | 3 | 4 | null
  case_id: string | null
  started_at: string | null
  ended_at: string | null
  outcome: EvaluationOutcome | null
}

export interface EvaluationEventV1 {
  event_id: string
  evaluation_session_id: string
  event: EvalEventName
  at: string
  metadata: Record<string, EvaluationPrimitive>
}

export interface EvaluationExportV1 {
  export_schema: typeof EVALUATION_EXPORT_SCHEMA
  exported_at: string
  participants: EvaluationParticipantV1[]
  sessions: EvaluationSessionV1[]
  events: EvaluationEventV1[]
}

export class EvalLogError extends Error {
  constructor(public readonly code: string, message: string) {
    super(message)
  }
}

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
  'evaluator_note',
  'evaluator_notes',
])

const SAFETY_BOOLEAN_KEYS = [
  'unsupported_fact',
  'leading_suggestion',
  'false_confidence',
  'critical_location_assertion',
  'critical_invented_recollection',
  'critical_forgetting_diagnosis',
  'critical_unsafe_action',
] as const

const HANDOFF_BOOLEAN_KEYS = [
  'mode_restored',
  'prior_checks_preserved',
  'journal_continuity',
  'next_action_coherent',
] as const

const EVENT_ALLOWED_KEYS: Record<EvalEventName, ReadonlySet<string>> = {
  case_started: new Set(['case_id']),
  next_action_shown: new Set(['case_id', 'candidate_id', 'proposal_id', 'mode']),
  next_action_started: new Set(['case_id', 'candidate_id', 'proposal_id', 'mode']),
  next_action_rejected: new Set(['case_id', 'candidate_id', 'proposal_id', 'reason_code']),
  check_started: new Set(['case_id', 'candidate_id', 'proposal_id', 'mode']),
  check_finished: new Set(['case_id', 'candidate_id', 'proposal_id', 'mode', 'outcome_code']),
  duplicate_check_detected: new Set(['case_id', 'candidate_id', 'proposal_id']),
  check_quality_clarified: new Set(['case_id', 'candidate_id', 'reason_code']),
  ai_guard_blocked: new Set(['case_id', 'guard_code']),
  assistant_offline_fallback: new Set(['case_id', 'reason_code', 'guard_code']),
  local_execution_failed: new Set(['case_id', 'command_id', 'reason_code', 'outcome_code']),
  pending_command_started: new Set(['case_id', 'command_id']),
  pending_command_retried: new Set(['case_id', 'command_id', 'reason_code']),
  pending_command_failed: new Set(['case_id', 'command_id', 'reason_code', 'outcome_code']),
  pause: new Set(['case_id']),
  resume: new Set(['case_id']),
  found: new Set(['case_id', 'outcome_code', 'found_context']),
  case_closed_unresolved: new Set(['case_id', 'outcome_code']),
  case_abandoned: new Set(['case_id']),
  found_context_recorded: new Set(['case_id', 'found_context']),
  post_case_rating: new Set(['task_load', 'convenience']),
  proposal_safety_annotation: new Set(['proposal_id', ...SAFETY_BOOLEAN_KEYS]),
  handoff_rubric: new Set([...HANDOFF_BOOLEAN_KEYS, 'handoff_score']),
}

const BOOLEAN_KEYS = new Set([...SAFETY_BOOLEAN_KEYS, ...HANDOFF_BOOLEAN_KEYS])
const ID_KEYS = new Set(['case_id', 'candidate_id', 'proposal_id', 'command_id'])
const ENUM_STRING_KEYS = new Set(['mode', 'reason_code', 'guard_code', 'outcome_code', 'found_context'])
const MAX_STRING_LENGTH = 256

export function validateRating(value: unknown): 1 | 2 | 3 | 4 | 5 {
  if (!Number.isInteger(value) || typeof value !== 'number' || value < 1 || value > 5) {
    throw new EvalLogError('MD_WEB_EVAL_RATING', 'evaluation rating must be an integer from 1 to 5')
  }
  return value as 1 | 2 | 3 | 4 | 5
}

function validateString(key: string, value: unknown): string {
  if (typeof value !== 'string' || value.length === 0 || value.length > MAX_STRING_LENGTH) {
    throw new EvalLogError('MD_WEB_EVAL_VALUE', `invalid evaluation string: ${key}`)
  }
  return value
}

export function validateEventMetadata(
  event: EvalEventName,
  metadata: Record<string, unknown> = {},
): Record<string, EvaluationPrimitive> {
  const allowed = EVENT_ALLOWED_KEYS[event]
  const safe: Record<string, EvaluationPrimitive> = {}

  for (const [key, value] of Object.entries(metadata)) {
    if (SENSITIVE_KEYS.has(key)) {
      throw new EvalLogError('MD_WEB_EVAL_SENSITIVE_FIELD', `sensitive evaluation field: ${key}`)
    }
    if (!allowed.has(key)) {
      throw new EvalLogError('MD_WEB_EVAL_FIELD', `unexpected evaluation field for ${event}: ${key}`)
    }

    if (key === 'task_load' || key === 'convenience') {
      safe[key] = validateRating(value)
      continue
    }
    if (key === 'handoff_score') {
      if (typeof value !== 'number' || !Number.isInteger(value) || value < 0 || value > 4) {
        throw new EvalLogError('MD_WEB_EVAL_HANDOFF_SCORE', 'handoff score must be an integer from 0 to 4')
      }
      safe[key] = value
      continue
    }
    if (BOOLEAN_KEYS.has(key)) {
      if (typeof value !== 'boolean') {
        throw new EvalLogError('MD_WEB_EVAL_VALUE', `invalid evaluation boolean: ${key}`)
      }
      safe[key] = value
      continue
    }
    if (ID_KEYS.has(key) || ENUM_STRING_KEYS.has(key)) {
      safe[key] = validateString(key, value)
      continue
    }
    if (value === null || ['string', 'number', 'boolean'].includes(typeof value)) {
      if (typeof value === 'string' && value.length > MAX_STRING_LENGTH) {
        throw new EvalLogError('MD_WEB_EVAL_VALUE', `evaluation string too long: ${key}`)
      }
      if (typeof value === 'number' && !Number.isFinite(value)) {
        throw new EvalLogError('MD_WEB_EVAL_VALUE', `invalid evaluation number: ${key}`)
      }
      safe[key] = value as EvaluationPrimitive
      continue
    }
    throw new EvalLogError('MD_WEB_EVAL_VALUE', `invalid evaluation value: ${key}`)
  }

  return safe
}

function validateId(code: string, value: string): void {
  if (value.length === 0 || value.length > 128) {
    throw new EvalLogError(code, `invalid evaluation identifier: ${value}`)
  }
}

export function validateEvaluationParticipant(participant: EvaluationParticipantV1): EvaluationParticipantV1 {
  if (participant.evaluation_schema !== EVALUATION_SCHEMA) throw new EvalLogError('MD_WEB_EVAL_SCHEMA', 'invalid participant schema')
  validateId('MD_WEB_EVAL_PARTICIPANT_ID', participant.participant_id)
  if (!['staged', 'real', 'external_a'].includes(participant.protocol)) throw new EvalLogError('MD_WEB_EVAL_PROTOCOL', 'invalid participant protocol')
  if (participant.enrollment_slot !== null && (!Number.isInteger(participant.enrollment_slot) || participant.enrollment_slot < 1)) {
    throw new EvalLogError('MD_WEB_EVAL_ENROLLMENT_SLOT', 'invalid enrollment slot')
  }
  if (participant.counterbalance_cell !== null && ![1, 2, 3, 4].includes(participant.counterbalance_cell)) {
    throw new EvalLogError('MD_WEB_EVAL_COUNTERBALANCE', 'invalid counterbalance cell')
  }
  return participant
}

export function validateEvaluationSession(session: EvaluationSessionV1): EvaluationSessionV1 {
  if (session.evaluation_schema !== EVALUATION_SCHEMA) throw new EvalLogError('MD_WEB_EVAL_SCHEMA', 'invalid session schema')
  validateId('MD_WEB_EVAL_SESSION_ID', session.evaluation_session_id)
  validateId('MD_WEB_EVAL_PARTICIPANT_ID', session.participant_id)
  if (session.assignment_version !== EVALUATION_ASSIGNMENT_VERSION) throw new EvalLogError('MD_WEB_EVAL_ASSIGNMENT_VERSION', 'invalid assignment version')

  if (session.protocol === 'external_a') {
    if (session.arm !== 'A') throw new EvalLogError('MD_WEB_EVAL_EXTERNAL_ARM', 'external A session must use arm A')
  } else if (session.arm !== 'B' && session.arm !== 'C') {
    throw new EvalLogError('MD_WEB_EVAL_APPLICATION_ARM', 'application evaluation session must use arm B or C')
  }

  if (session.protocol === 'staged') {
    if (session.counterbalance_cell === null || session.scenario_family === null || session.scenario_variant === null || session.order_position === null) {
      throw new EvalLogError('MD_WEB_EVAL_STAGED_ASSIGNMENT', 'staged session requires complete assignment metadata')
    }
  }

  if (session.protocol === 'real') {
    if (session.counterbalance_cell !== null || session.scenario_family !== null || session.scenario_variant !== null || session.order_position !== null) {
      throw new EvalLogError('MD_WEB_EVAL_REAL_ASSIGNMENT', 'real session must not contain staged assignment metadata')
    }
  }

  if (session.case_id !== null) validateId('MD_WEB_EVAL_CASE_ID', session.case_id)
  return session
}
