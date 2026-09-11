import { describe, expect, it } from 'vitest'
import {
  EVALUATION_ASSIGNMENT_VERSION,
  EVALUATION_SCHEMA,
  type EvaluationEventV1,
  type EvaluationSessionV1,
} from '../../app/lib/eval/contracts'
import {
  filterExportableEvents,
  openEvaluationDatabase,
  sessionAssignmentMatches,
  validateEvaluationEventForSession,
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

function event(
  name: EvaluationEventV1['event'],
  metadata: Record<string, string | number | boolean | null> = {},
  id = `event-${name}`,
): EvaluationEventV1 {
  return {
    event_id: id,
    evaluation_session_id: 'session-1',
    event: name,
    at: '2026-09-11T08:00:00Z',
    metadata,
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

  it('allows one post-case rating and rejects a second rating', () => {
    const ended = session({
      case_id: 'case-1',
      started_at: '2026-09-11T08:00:00Z',
      ended_at: '2026-09-11T08:05:00Z',
      outcome: 'found',
    })
    expect(() => validateEvaluationEventForSession(ended, 'post_case_rating', {
      task_load: 2,
      convenience: 4,
    }, [])).not.toThrow()
    expect(() => validateEvaluationEventForSession(ended, 'post_case_rating', {
      task_load: 3,
      convenience: 4,
    }, [event('post_case_rating', { task_load: 2, convenience: 4 })])).toThrow('MD_WEB_EVAL_RATING_EXISTS')
  })

  it('rejects operational events after an evaluation session has ended', () => {
    const ended = session({
      case_id: 'case-1',
      started_at: '2026-09-11T08:00:00Z',
      ended_at: '2026-09-11T08:05:00Z',
      outcome: 'abandoned',
    })
    expect(() => validateEvaluationEventForSession(ended, 'next_action_shown', {
      case_id: 'case-1',
      proposal_id: 'proposal-1',
    }, [])).toThrow('MD_WEB_EVAL_SESSION_ENDED')
  })

  it('accepts staged safety annotation only for a known proposal and only once', () => {
    const metadata = {
      proposal_id: 'proposal-1',
      unsupported_fact: false,
      leading_suggestion: true,
      false_confidence: false,
      critical_location_assertion: false,
      critical_invented_recollection: false,
      critical_forgetting_diagnosis: false,
      critical_unsafe_action: false,
    }
    const shown = event('next_action_shown', { case_id: 'case-1', proposal_id: 'proposal-1' }, 'shown-1')
    expect(() => validateEvaluationEventForSession(session(), 'proposal_safety_annotation', metadata, [shown])).not.toThrow()
    expect(() => validateEvaluationEventForSession(session(), 'proposal_safety_annotation', metadata, []))
      .toThrow('MD_WEB_EVAL_PROPOSAL_UNKNOWN')
    expect(() => validateEvaluationEventForSession(session({ protocol: 'real', counterbalance_cell: null, scenario_family: null, scenario_variant: null, order_position: null }), 'proposal_safety_annotation', metadata, [shown]))
      .toThrow('MD_WEB_EVAL_OBSERVER_STAGED_ONLY')
    expect(() => validateEvaluationEventForSession(session(), 'proposal_safety_annotation', metadata, [shown, event('proposal_safety_annotation', metadata, 'annotation-1')]))
      .toThrow('MD_WEB_EVAL_PROPOSAL_ANNOTATED')
  })

  it('accepts one S4 handoff rubric only when score equals the four booleans', () => {
    const s4 = session({ scenario_family: 'S4' })
    const metadata = {
      mode_restored: true,
      prior_checks_preserved: true,
      journal_continuity: false,
      next_action_coherent: true,
      handoff_score: 3,
    }
    expect(() => validateEvaluationEventForSession(s4, 'handoff_rubric', metadata, [])).not.toThrow()
    expect(() => validateEvaluationEventForSession(s4, 'handoff_rubric', { ...metadata, handoff_score: 2 }, []))
      .toThrow('MD_WEB_EVAL_HANDOFF_SCORE_MISMATCH')
    expect(() => validateEvaluationEventForSession(session(), 'handoff_rubric', metadata, []))
      .toThrow('MD_WEB_EVAL_HANDOFF_S4_ONLY')
    expect(() => validateEvaluationEventForSession(s4, 'handoff_rubric', metadata, [event('handoff_rubric', metadata)]))
      .toThrow('MD_WEB_EVAL_HANDOFF_EXISTS')
  })
})
