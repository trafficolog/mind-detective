import {
  EVALUATION_ASSIGNMENT_VERSION,
  EVALUATION_SCHEMA,
  type CounterbalanceCell,
  type EvaluationArm,
  type EvaluationParticipantV1,
  type EvaluationSessionV1,
  type ScenarioFamily,
  type ScenarioVariant,
} from './contracts'

export interface StagedAssignment {
  family: ScenarioFamily
  arm: Exclude<EvaluationArm, 'A'>
  variant: ScenarioVariant
  order_position: 1 | 2 | 3 | 4
}

export const STAGED_CELLS: Readonly<Record<CounterbalanceCell, readonly StagedAssignment[]>> = {
  1: [
    { family: 'S1', arm: 'B', variant: 'A', order_position: 1 },
    { family: 'S2', arm: 'C', variant: 'A', order_position: 2 },
    { family: 'S3', arm: 'B', variant: 'A', order_position: 3 },
    { family: 'S4', arm: 'C', variant: 'A', order_position: 4 },
  ],
  2: [
    { family: 'S2', arm: 'B', variant: 'B', order_position: 1 },
    { family: 'S3', arm: 'C', variant: 'B', order_position: 2 },
    { family: 'S4', arm: 'B', variant: 'B', order_position: 3 },
    { family: 'S1', arm: 'C', variant: 'A', order_position: 4 },
  ],
  3: [
    { family: 'S3', arm: 'C', variant: 'A', order_position: 1 },
    { family: 'S4', arm: 'B', variant: 'A', order_position: 2 },
    { family: 'S1', arm: 'C', variant: 'B', order_position: 3 },
    { family: 'S2', arm: 'B', variant: 'A', order_position: 4 },
  ],
  4: [
    { family: 'S4', arm: 'C', variant: 'B', order_position: 1 },
    { family: 'S1', arm: 'B', variant: 'B', order_position: 2 },
    { family: 'S2', arm: 'C', variant: 'B', order_position: 3 },
    { family: 'S3', arm: 'B', variant: 'B', order_position: 4 },
  ],
}

export function cellForEnrollmentSlot(slot: number): CounterbalanceCell {
  if (!Number.isInteger(slot) || slot < 1) throw new Error('MD_WEB_EVAL_ENROLLMENT_SLOT')
  return (((slot - 1) % 4) + 1) as CounterbalanceCell
}

export function createStagedParticipantRecord(
  enrollmentSlot: number,
  participantId = crypto.randomUUID(),
  createdAt = new Date().toISOString(),
): EvaluationParticipantV1 {
  return {
    evaluation_schema: EVALUATION_SCHEMA,
    participant_id: participantId,
    protocol: 'staged',
    enrollment_slot: enrollmentSlot,
    counterbalance_cell: cellForEnrollmentSlot(enrollmentSlot),
    created_at: createdAt,
  }
}

function stagedSessionsForParticipant(
  participant: EvaluationParticipantV1,
  sessions: readonly EvaluationSessionV1[],
): EvaluationSessionV1[] {
  return sessions.filter(session => session.participant_id === participant.participant_id && session.protocol === 'staged')
}

export function nextStagedAssignment(
  participant: EvaluationParticipantV1,
  existingSessions: readonly EvaluationSessionV1[],
): StagedAssignment | null {
  if (participant.protocol !== 'staged' || participant.counterbalance_cell === null) {
    throw new Error('MD_WEB_EVAL_STAGED_PARTICIPANT')
  }

  const sessions = stagedSessionsForParticipant(participant, existingSessions)
  for (const session of sessions) {
    if (session.counterbalance_cell !== participant.counterbalance_cell) {
      throw new Error('MD_WEB_EVAL_COUNTERBALANCE_DRIFT')
    }
  }

  const usedPositions = new Set(sessions.map(session => session.order_position))
  return STAGED_CELLS[participant.counterbalance_cell]
    .find(assignment => !usedPositions.has(assignment.order_position)) ?? null
}

export function stagedSessionFromAssignment(
  participant: EvaluationParticipantV1,
  assignment: StagedAssignment,
  evaluationSessionId = crypto.randomUUID(),
): EvaluationSessionV1 {
  if (participant.protocol !== 'staged' || participant.counterbalance_cell === null) {
    throw new Error('MD_WEB_EVAL_STAGED_PARTICIPANT')
  }
  return {
    evaluation_schema: EVALUATION_SCHEMA,
    evaluation_session_id: evaluationSessionId,
    participant_id: participant.participant_id,
    protocol: 'staged',
    arm: assignment.arm,
    assignment_version: EVALUATION_ASSIGNMENT_VERSION,
    counterbalance_cell: participant.counterbalance_cell,
    scenario_family: assignment.family,
    scenario_variant: assignment.variant,
    order_position: assignment.order_position,
    case_id: null,
    started_at: null,
    ended_at: null,
    outcome: null,
  }
}

export function assignRealArm(randomByte?: number): 'B' | 'C' {
  const byte = randomByte ?? crypto.getRandomValues(new Uint8Array(1))[0]!
  if (!Number.isInteger(byte) || byte < 0 || byte > 255) throw new Error('MD_WEB_EVAL_RANDOM_BYTE')
  return byte % 2 === 0 ? 'B' : 'C'
}

export function createRealParticipantRecord(
  participantId = crypto.randomUUID(),
  createdAt = new Date().toISOString(),
): EvaluationParticipantV1 {
  return {
    evaluation_schema: EVALUATION_SCHEMA,
    participant_id: participantId,
    protocol: 'real',
    enrollment_slot: null,
    counterbalance_cell: null,
    created_at: createdAt,
  }
}

export function createRealSession(
  participant: EvaluationParticipantV1,
  arm: 'B' | 'C',
  evaluationSessionId = crypto.randomUUID(),
): EvaluationSessionV1 {
  if (participant.protocol !== 'real') throw new Error('MD_WEB_EVAL_REAL_PARTICIPANT')
  return {
    evaluation_schema: EVALUATION_SCHEMA,
    evaluation_session_id: evaluationSessionId,
    participant_id: participant.participant_id,
    protocol: 'real',
    arm,
    assignment_version: EVALUATION_ASSIGNMENT_VERSION,
    counterbalance_cell: null,
    scenario_family: null,
    scenario_variant: null,
    order_position: null,
    case_id: null,
    started_at: null,
    ended_at: null,
    outcome: null,
  }
}
