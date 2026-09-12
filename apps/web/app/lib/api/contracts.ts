export type CaseLifecycle = 'active' | 'paused' | 'closed_found' | 'closed_unresolved' | 'deleted'
export type InteractionMode = 'unselected' | 'reconstruction' | 'search'
export type JournalMode = 'reconstruction' | 'search' | 'system'
export type JournalAuthor = 'user' | 'assistant' | 'system'
export type SearchMethod = 'reported_check' | 'glance' | 'visual_systematic' | 'empty_and_check' | 'tactile' | 'inaccessible'
export type SearchResult = 'found' | 'not_found' | 'partial' | 'inaccessible'
export type CheckState = 'unchecked' | 'partial' | 'checked'
export type ExperimentalArm = 'checklist' | 'assistant'
export type ProposalCopyKey =
  | 'reconstruction.clarify_supported_sequence'
  | 'next_action.check_target'
  | 'empty.resolve_partial_check'
  | 'empty.add_supported_place_or_reconstruct'

export interface StatementV2 {
  id: string
  source: 'user' | 'file' | 'assistant'
  statement_type: 'recollection' | 'habit' | 'observation' | 'hypothesis' | 'search_suggestion'
  original_text: string
  recorded_at: string
  event_time: string | null
  user_confirmation: boolean
  supporting_evidence_ids: string[]
  limitations: string[]
}

export interface TimelineEventV2 {
  id: string
  label: string
  statement_ids: string[]
  event_time: string | null
  time_precision: string
}

export interface TimelineV2 {
  last_supported_interaction_id: string | null
  first_noticed_missing_id: string | null
  events: TimelineEventV2[]
  unknown_intervals: string[]
  contradictions: string[]
}

export interface SearchCheckV2 {
  id: string
  target: string
  method: SearchMethod
  started_at: string
  completed_at: string | null
  result: SearchResult
  inaccessible_parts: string[]
  based_on: string[]
  notes: string[]
}

export interface CandidateCheckV2 {
  id: string
  target: string
  route_relation: 'direct' | 'indirect' | 'none'
  check_state: CheckState
  effort: 'low' | 'medium' | 'high'
  safety: 'safe' | 'caution' | 'unsafe'
  urgency_relevance: 'high' | 'normal'
  basis: 'episode' | 'habit' | 'generic'
  based_on: string[]
  rationale: string[]
}

export interface NextActionV2 {
  candidate_id: string
  target: string
  rationale_codes: string[]
}

export interface JournalEntryV2 {
  id: string
  author: JournalAuthor
  mode: JournalMode
  entry_type: string
  text: string
  created_at: string
  statement_ids: string[]
  search_check_ids: string[]
}

export interface ActionFeedbackV2 {
  id: string
  candidate_id: string
  reason: 'already_checked' | 'impossible_now' | 'irrelevant' | 'unsafe_or_uncomfortable' | 'other'
  recorded_at: string
}

export interface CaseV2 {
  schema: 'mind-detective-case/v2'
  case_id: string
  item_label: string
  created_at: string
  updated_at: string
  lifecycle: CaseLifecycle
  statements: StatementV2[]
  timeline: TimelineV2 | null
  search_checks: SearchCheckV2[]
  candidates: CandidateCheckV2[]
  next_action: NextActionV2 | null
  constraints: string[]
  outcome: Record<string, unknown> | null
  current_mode: InteractionMode
  interaction_journal: JournalEntryV2[]
  action_feedback: ActionFeedbackV2[]
}

export interface CommandEnvelope {
  command_id: string
  expected_updated_at: string
  command_type: 'set_mode' | 'add_statement' | 'record_search_check' | 'refine_search_check' | 'reject_next_action' | 'pause' | 'resume' | 'close_found' | 'close_unresolved'
  now: string
  payload: Record<string, unknown>
}

export interface ProposalModel {
  kind: 'next_action' | 'clarification' | 'need_more_information' | 'fallback'
  candidate_id: string | null
  target: string | null
  copy_key: ProposalCopyKey
  rationale_codes: string[]
  related_statement_ids: string[]
}

export interface ProposalResponse {
  case: CaseV2
  proposal: ProposalModel
  guard_code: string | null
}

export interface ExecutionIdentity {
  version: string
  kernel_sha256: string
  generated_sha256: string
  generator_version: string
}
