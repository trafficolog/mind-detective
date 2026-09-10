import { describe, expect, it } from 'vitest'
import { derivePriorCheckAnnotation, deriveProgress } from '../../app/lib/case/derived'
import type { CandidateCheckV2, CaseV2 } from '../../app/lib/api/contracts'

function candidate(id: string, state: CandidateCheckV2['check_state']): CandidateCheckV2 {
  return {
    id,
    target: `target-${id}`,
    route_relation: 'direct',
    check_state: state,
    effort: 'low',
    safety: 'safe',
    urgency_relevance: 'normal',
    basis: 'episode',
    based_on: [],
    rationale: [],
  }
}

function fixture(): CaseV2 {
  return {
    schema: 'mind-detective-case/v2',
    case_id: 'case-1',
    item_label: 'ключи',
    created_at: '2026-09-10T07:00:00Z',
    updated_at: '2026-09-10T07:01:00Z',
    lifecycle: 'active',
    statements: [],
    timeline: null,
    search_checks: [
      {
        id: 'check-inaccessible',
        target: 'target-c8',
        method: 'reported_check',
        started_at: '2026-09-10T07:00:30Z',
        completed_at: '2026-09-10T07:01:00Z',
        result: 'partial',
        inaccessible_parts: ['locked pocket'],
        based_on: ['c8'],
        notes: [],
      },
    ],
    candidates: [
      candidate('c1', 'checked'), candidate('c2', 'checked'), candidate('c3', 'checked'), candidate('c4', 'checked'),
      candidate('c5', 'unchecked'), candidate('c6', 'partial'), candidate('c7', 'unchecked'), candidate('c8', 'partial'),
    ],
    next_action: null,
    constraints: [],
    outcome: null,
    current_mode: 'search',
    interaction_journal: [],
    action_feedback: [],
  }
}

describe('read-only case derivations', () => {
  it('derives progress without mutating the case', () => {
    const caseValue = fixture()
    const before = structuredClone(caseValue)
    expect(deriveProgress(caseValue)).toEqual({ checked: 4, remaining: 3, inaccessible: 1 })
    expect(caseValue).toEqual(before)
  })

  it('uses explicit candidate ids for prior-check annotations', () => {
    const caseValue = fixture()
    expect(derivePriorCheckAnnotation(caseValue, 'c8')).toEqual({
      check_id: 'check-inaccessible',
      method: 'reported_check',
      result: 'partial',
      inaccessible_parts: ['locked pocket'],
      completed_at: '2026-09-10T07:01:00Z',
    })
    expect(derivePriorCheckAnnotation(caseValue, 'similar-target-text')).toBeNull()
  })
})
