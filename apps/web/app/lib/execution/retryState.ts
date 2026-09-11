import type { CaseV2, CommandEnvelope } from '../api/contracts'

export interface RetryableCommand {
  caseSnapshot: CaseV2
  command: CommandEnvelope
}

export function captureRetryableCommand(
  caseSnapshot: CaseV2,
  command: CommandEnvelope,
): RetryableCommand {
  return {
    caseSnapshot: structuredClone(caseSnapshot),
    command: structuredClone(command),
  }
}

export function cloneRetryableCommand(state: RetryableCommand): RetryableCommand {
  return {
    caseSnapshot: structuredClone(state.caseSnapshot),
    command: structuredClone(state.command),
  }
}
