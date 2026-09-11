import { describe, expect, it } from 'vitest'
import {
  EVALUATION_ASSIGNMENT_VERSION,
  EVALUATION_SCHEMA,
  type EvaluationSessionV1,
} from '../../app/lib/eval/contracts'
import {
  filterExportableEvents,
  openEvaluationDatabase,
  sessionAssignmentMatches,
} from '../../app/lib/eval/store'

function session(overrides: Partial<EvaluationSessionV1> = {}): EvaluationSessionV1 {
  return {
    evaluation_schema: EVALUATION_SCHEMA,
    evaluation_session_id: 'session-1',
    participant_id: 'participant-1',
    protocol: 'staged',
    arm: 'B',
    assignment_version: EVALUATION_ASSIGNMENT_VERSION,
    counterbalance_cell: 1,
    scenario_family: 'S1',
    scenario_variant: 'A',
    order_position: 1,
    case_id: null,
    started_at: null,
    ended_at: null,
    outcome: null,
    ...overrides,
  }
}

describe('evaluation store invariants', () => {
  it('fails closed when IndexedDB is unavailable in the unit-test runtime', async () => {
    await expect(openEvaluationDatabase()).rejects.toThrow('MD_WEB_EVAL_IDB_UNAVAILABLE')
  })

  it('treats assignment fields as immutable while allowing lifecycle fields to differ', () => {
    const original = session()
    expect(sessionAssignmentMatches(original, session({
      case_id: 'case-1',
      started_at: '2026-09-11T08:00:00Z',
      ended_at: '2026-09-11T08:05:00Z',
      outcome: 'found',
    }))).toBe(true)
    expect(sessionAssignmentMatches(original, session({ arm: 'C' }))).toBe(false)
    expect(sessionAssignmentMatches(original, session({ scenario_variant: 'B' }))).toBe(false)
  })

  it('excludes legacy unbound events from the v1 export event set', () => {
    const exported = filterExportableEvents([session()], [
      {
        event_id: 'legacy-event',
        event: 'found',
        at: '2026-09-11T07:59:59Z',
        metadata: { case_id: 'legacy-case' },
      },
      {
        event_id: 'bound-event',
        evaluation_session_id: 'session-1',
        event: 'case_started',
        at: '2026-09-11T08:00:00Z',
        metadata: { case_id: 'case-1' },
      },
      {
        event_id: 'orphan-event',
        evaluation_session_id: 'missing-session',
        event: 'case_started',
        at: '2026-09-11T08:00:01Z',
        metadata: { case_id: 'case-2' },
      },
    ])

    expect(exported).toHaveLength(1)
    expect(exported[0]?.event_id).toBe('bound-event')
    expect(exported[0]?.evaluation_session_id).toBe('session-1')
  })
})
