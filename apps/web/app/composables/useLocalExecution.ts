import { toRaw } from 'vue'
import type { CaseV2, CommandEnvelope, ProposalModel } from '~/lib/api/contracts'
import {
  applyLocalCommand,
  buildLocalChecklistProposal,
  createLocalSearchCase,
} from '~/lib/execution/localExecutor'
import { enforceSafeInput } from '~/lib/safety'

export interface LocalExecution {
  createCase(caseId: string, itemLabel: string, now: string): Promise<CaseV2>
  sendCommand(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2>
  checklistProposal(caseValue: CaseV2): ProposalModel
}

function plainCase(caseValue: CaseV2): CaseV2 {
  return structuredClone(toRaw(caseValue))
}

function enforceCommandIngress(command: CommandEnvelope): void {
  const text = command.command_type === 'add_statement'
    ? command.payload.original_text
    : command.command_type === 'record_free_account'
      ? command.payload.text
      : null
  if (typeof text === 'string') enforceSafeInput(text)
}

export function useLocalExecution(): LocalExecution {
  const repository = useCaseRepository()

  async function createCase(caseId: string, itemLabel: string, now: string): Promise<CaseV2> {
    enforceSafeInput(itemLabel)
    return await createLocalSearchCase(repository, caseId, itemLabel, now)
  }

  async function sendCommand(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2> {
    enforceCommandIngress(command)
    return await applyLocalCommand(repository, plainCase(caseValue), command)
  }

  function checklistProposal(caseValue: CaseV2): ProposalModel {
    return buildLocalChecklistProposal(plainCase(caseValue), 'search')
  }

  return { createCase, sendCommand, checklistProposal }
}
