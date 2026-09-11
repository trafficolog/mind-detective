import type { ExperimentalArm } from '~/lib/api/contracts'
import type { EvaluationSessionV1 } from '~/lib/eval/contracts'
import {
  assignRealArm,
  createRealParticipantRecord,
  createRealSession,
  createStagedParticipantRecord,
  nextStagedAssignment,
  stagedSessionFromAssignment,
} from '~/lib/eval/assignment'
import {
  createEvaluationParticipant,
  createEvaluationSession,
  getEvaluationSessionByCaseId,
  listEvaluationParticipants,
  listEvaluationSessions,
} from '~/lib/eval/store'

function requireEvaluationEnabled(): void {
  const config = useRuntimeConfig()
  if (config.public.mindDetectiveEvaluationEnabled !== true) {
    throw new Error('MD_WEB_EVAL_DISABLED')
  }
}

export function useEvaluationSession() {
  const session = useState<EvaluationSessionV1 | null>('mind-detective-evaluation-session', () => null)

  async function loadForCase(caseId: string): Promise<EvaluationSessionV1 | null> {
    requireEvaluationEnabled()
    session.value = await getEvaluationSessionByCaseId(caseId)
    return session.value
  }

  function clear(): void {
    session.value = null
  }

  function effectiveProductArm(value: EvaluationSessionV1 = session.value as EvaluationSessionV1): ExperimentalArm {
    if (!value) throw new Error('MD_WEB_EVAL_SESSION_NOT_LOADED')
    if (value.arm === 'B') return 'checklist'
    if (value.arm === 'C') return 'assistant'
    throw new Error('MD_WEB_EVAL_EXTERNAL_ARM')
  }

  async function startStagedSession(enrollmentSlot: number): Promise<EvaluationSessionV1> {
    requireEvaluationEnabled()
    const participants = await listEvaluationParticipants()
    const matches = participants.filter(participant => participant.protocol === 'staged' && participant.enrollment_slot === enrollmentSlot)
    if (matches.length > 1) throw new Error('MD_WEB_EVAL_ENROLLMENT_DUPLICATE')

    let participant = matches[0]
    if (!participant) {
      participant = createStagedParticipantRecord(enrollmentSlot)
      await createEvaluationParticipant(participant)
    }

    const allSessions = await listEvaluationSessions()
    const participantSessions = allSessions.filter(value => value.participant_id === participant.participant_id)
    const active = participantSessions.find(value => value.ended_at === null)
    if (active) {
      session.value = active
      return active
    }

    const assignment = nextStagedAssignment(participant, participantSessions)
    if (!assignment) throw new Error('MD_WEB_EVAL_STAGED_COMPLETE')
    const created = stagedSessionFromAssignment(participant, assignment)
    await createEvaluationSession(created)
    session.value = created
    return created
  }

  async function startRealSession(randomByte?: number): Promise<EvaluationSessionV1> {
    requireEvaluationEnabled()
    const participant = createRealParticipantRecord()
    await createEvaluationParticipant(participant)
    const created = createRealSession(participant, assignRealArm(randomByte))
    await createEvaluationSession(created)
    session.value = created
    return created
  }

  return {
    session,
    loadForCase,
    clear,
    effectiveProductArm,
    startStagedSession,
    startRealSession,
  }
}
