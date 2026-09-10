import type { CaseV2, CommandEnvelope, ProposalModel } from '~/lib/api/contracts'
import {
  applyLocalCommand,
  buildLocalChecklistProposal,
  createLocalCase,
} from '~/lib/execution/localExecutor'

export interface LocalExecution {
  createCase(caseId: string, itemLabel: string, now: string): Promise<CaseV2>
  sendCommand(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2>
  checklistProposal(caseValue: CaseV2, mode: 'reconstruction' | 'search'): ProposalModel
}

export function useLocalExecution(): LocalExecution {
  const repository = useCaseRepository()

  async function createCase(caseId: string, itemLabel: string, now: string): Promise<CaseV2> {
    return await createLocalCase(repository, caseId, itemLabel, now)
  }

  async function sendCommand(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2> {
    return await applyLocalCommand(repository, caseValue, command)
  }

  function checklistProposal(caseValue: CaseV2, mode: 'reconstruction' | 'search'): ProposalModel {
    return buildLocalChecklistProposal(caseValue, mode)
  }

  return { createCase, sendCommand, checklistProposal }
}
