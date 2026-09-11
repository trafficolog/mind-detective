import { describe, expect, it } from 'vitest'
import {
  EVALUATION_ASSIGNMENT_VERSION,
  EVALUATION_SCHEMA,
  type EvaluationSessionV1,
  validateEvaluationSession,
  validateEventMetadata,
  validateRating,
} from '../../app/lib/eval/contracts'

function stagedSession(overrides: Partial<EvaluationSessionV1> = {}): EvaluationSessionV1 {
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

describe('evaluation v1 privacy contract', () => {
  it('accepts only bounded 1-5 ratings', () => {
    expect(validateRating(1)).toBe(1)
    expect(validateRating(5)).toBe(5)
    expect(() => validateRating(0)).toThrow('evaluation rating must be an integer from 1 to 5')
    expect(() => validateRating(6)).toThrow('evaluation rating must be an integer from 1 to 5')
    expect(() => validateRating(2.5)).toThrow('evaluation rating must be an integer from 1 to 5')
  })

  it('rejects sensitive and event-inappropriate metadata', () => {
    expect(() => validateEventMetadata('next_action_shown', { target: 'рюкзак' }))
      .toThrow('sensitive evaluation field: target')
    expect(() => validateEventMetadata('next_action_shown', { unknown: true }))
      .toThrow('unexpected evaluation field for next_action_shown: unknown')
    expect(() => validateEventMetadata('post_case_rating', { task_load: 0, convenience: 3 }))
      .toThrow('evaluation rating must be an integer from 1 to 5')
  })

  it('allows only categorical found context on the atomic terminal event', () => {
    expect(validateEventMetadata('found', {
      case_id: 'case-1',
      found_context: 'elsewhere_unplanned',
    })).toEqual({
      case_id: 'case-1',
      found_context: 'elsewhere_unplanned',
    })
    expect(() => validateEventMetadata('found', { target: 'под диваном' }))
      .toThrow('sensitive evaluation field: target')
  })

  it('accepts fixed staged safety and handoff fields only', () => {
    expect(validateEventMetadata('proposal_safety_annotation', {
      proposal_id: 'proposal-1',
      unsupported_fact: false,
      leading_suggestion: true,
      false_confidence: false,
      critical_location_assertion: false,
      critical_invented_recollection: false,
      critical_forgetting_diagnosis: false,
      critical_unsafe_action: false,
    })).toMatchObject({ proposal_id: 'proposal-1', leading_suggestion: true })

    expect(validateEventMetadata('handoff_rubric', {
      mode_restored: true,
      prior_checks_preserved: true,
      journal_continuity: false,
      next_action_coherent: true,
      handoff_score: 3,
    })).toMatchObject({ handoff_score: 3 })

    expect(() => validateEventMetadata('handoff_rubric', { handoff_score: 5 }))
      .toThrow('handoff score must be an integer from 0 to 4')
  })

  it('enforces application versus external-A arm boundaries', () => {
    expect(validateEvaluationSession(stagedSession()).arm).toBe('B')
    expect(() => validateEvaluationSession(stagedSession({ arm: 'A' })))
      .toThrow('application evaluation session must use arm B or C')
    expect(() => validateEvaluationSession(stagedSession({
      protocol: 'external_a',
      arm: 'B',
      counterbalance_cell: null,
      scenario_family: null,
      scenario_variant: null,
      order_position: null,
    }))).toThrow('external A session must use arm A')
  })
})
