import { describe, expect, it } from 'vitest'
import {
  STAGED_CELLS,
  assignRealArm,
  cellForEnrollmentSlot,
  createRealParticipantRecord,
  createRealSession,
  createStagedParticipantRecord,
  nextStagedAssignment,
  stagedSessionFromAssignment,
} from '../../app/lib/eval/assignment'
import type { EvaluationSessionV1, ScenarioFamily } from '../../app/lib/eval/contracts'

function allAssignmentsFor(family: ScenarioFamily) {
  return ([1, 2, 3, 4] as const)
    .flatMap(cell => STAGED_CELLS[cell])
    .filter(assignment => assignment.family === family)
}

describe('staged evaluation assignment', () => {
  it('keeps two B and two C tasks inside every counterbalance cell', () => {
    for (const cell of [1, 2, 3, 4] as const) {
      const assignments = STAGED_CELLS[cell]
      expect(assignments).toHaveLength(4)
      expect(assignments.filter(assignment => assignment.arm === 'B')).toHaveLength(2)
      expect(assignments.filter(assignment => assignment.arm === 'C')).toHaveLength(2)
      expect(assignments.map(assignment => assignment.order_position)).toEqual([1, 2, 3, 4])
    }
  })

  it('gives every family every arm by variant combination exactly once across cells', () => {
    for (const family of ['S1', 'S2', 'S3', 'S4'] as const) {
      const assignments = allAssignmentsFor(family)
      expect(assignments).toHaveLength(4)
      const combinations = new Set(assignments.map(assignment => `${assignment.arm}/${assignment.variant}`))
      expect(combinations).toEqual(new Set(['B/A', 'B/B', 'C/A', 'C/B']))
    }
  })

  it('balances first arm two B versus two C across cells', () => {
    expect(STAGED_CELLS[1][0]?.arm).toBe('B')
    expect(STAGED_CELLS[2][0]?.arm).toBe('B')
    expect(STAGED_CELLS[3][0]?.arm).toBe('C')
    expect(STAGED_CELLS[4][0]?.arm).toBe('C')
  })

  it('derives counterbalance cell from preassigned enrollment slot', () => {
    expect(cellForEnrollmentSlot(1)).toBe(1)
    expect(cellForEnrollmentSlot(4)).toBe(4)
    expect(cellForEnrollmentSlot(5)).toBe(1)
    expect(cellForEnrollmentSlot(10)).toBe(2)
    expect(() => cellForEnrollmentSlot(0)).toThrow('MD_WEB_EVAL_ENROLLMENT_SLOT')
    expect(() => cellForEnrollmentSlot(1.5)).toThrow('MD_WEB_EVAL_ENROLLMENT_SLOT')
  })

  it('creates staged participant and sessions from the frozen cell', () => {
    const participant = createStagedParticipantRecord(3, 'participant-3', '2026-09-11T08:00:00Z')
    expect(participant.counterbalance_cell).toBe(3)
    const first = nextStagedAssignment(participant, [])
    expect(first).toEqual({ family: 'S3', arm: 'C', variant: 'A', order_position: 1 })
    const session = stagedSessionFromAssignment(participant, first!, 'session-1')
    expect(session.arm).toBe('C')
    expect(session.scenario_family).toBe('S3')
    expect(session.counterbalance_cell).toBe(3)
  })

  it('returns first missing order position and ignores other participants', () => {
    const participant = createStagedParticipantRecord(1, 'participant-1', '2026-09-11T08:00:00Z')
    const first = stagedSessionFromAssignment(participant, STAGED_CELLS[1][0]!, 'session-1')
    const unrelated: EvaluationSessionV1 = { ...first, evaluation_session_id: 'session-other', participant_id: 'participant-other' }
    expect(nextStagedAssignment(participant, [unrelated])?.order_position).toBe(1)
    expect(nextStagedAssignment(participant, [first])?.order_position).toBe(2)

    const all = STAGED_CELLS[1].map((assignment, index) => stagedSessionFromAssignment(participant, assignment, `session-${index + 1}`))
    expect(nextStagedAssignment(participant, all)).toBeNull()
  })

  it('fails closed when stored staged sessions drift to another cell', () => {
    const participant = createStagedParticipantRecord(1, 'participant-1', '2026-09-11T08:00:00Z')
    const drifted = stagedSessionFromAssignment(participant, STAGED_CELLS[1][0]!, 'session-1')
    drifted.counterbalance_cell = 2
    expect(() => nextStagedAssignment(participant, [drifted])).toThrow('MD_WEB_EVAL_COUNTERBALANCE_DRIFT')
  })
})

describe('real evaluation assignment', () => {
  it('maps even entropy to B and odd entropy to C', () => {
    expect(assignRealArm(0)).toBe('B')
    expect(assignRealArm(254)).toBe('B')
    expect(assignRealArm(1)).toBe('C')
    expect(assignRealArm(255)).toBe('C')
    expect(() => assignRealArm(256)).toThrow('MD_WEB_EVAL_RANDOM_BYTE')
  })

  it('creates a one-time real session record with no staged metadata', () => {
    const participant = createRealParticipantRecord('participant-real', '2026-09-11T09:00:00Z')
    const session = createRealSession(participant, assignRealArm(11), 'session-real')
    expect(session.arm).toBe('C')
    expect(session.counterbalance_cell).toBeNull()
    expect(session.scenario_family).toBeNull()
    expect(session.order_position).toBeNull()
  })
})
