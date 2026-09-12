import type { CaseV2, CommandEnvelope, ProposalModel } from '../api/contracts'
import {
  LOCAL_EXECUTION_CONTRACT,
  apply_command,
  build_checklist_proposal_json,
  create_case,
} from '../../generated/localExecution'
import { canonicalSha256 } from './canonicalJson'
import type { ExecutionReceipt } from '../storage/indexeddb'
import { receiptInputMatches } from '../storage/indexeddb'

export interface LocalExecutionRepository {
  get(caseId: string): Promise<CaseV2 | null>
  createOnly(caseValue: CaseV2): Promise<CaseV2>
  getReceipt(commandId: string): Promise<ExecutionReceipt | null>
  applyWithReceipt(caseValue: CaseV2, receipt: ExecutionReceipt): Promise<CaseV2>
}

export async function createLocalCase(
  repository: LocalExecutionRepository,
  caseId: string,
  itemLabel: string,
  now: string,
): Promise<CaseV2> {
  const created = create_case(caseId, itemLabel, now) as CaseV2
  return await repository.createOnly(created)
}

export async function createLocalSearchCase(
  repository: LocalExecutionRepository,
  caseId: string,
  itemLabel: string,
  now: string,
): Promise<CaseV2> {
  const created = create_case(caseId, itemLabel, now) as CaseV2
  const searchCase = apply_command(
    structuredClone(created) as unknown as Record<string, unknown>,
    {
      command_id: `initial-search:${caseId}`,
      expected_updated_at: created.updated_at,
      command_type: 'set_mode',
      now,
      payload: { mode: 'search' },
    },
  ) as CaseV2
  return await repository.createOnly(searchCase)
}

export async function applyLocalCommand(
  repository: LocalExecutionRepository,
  caseValue: CaseV2,
  command: CommandEnvelope,
): Promise<CaseV2> {
  const inputCaseHash = await canonicalSha256(caseValue)
  const existingReceipt = await repository.getReceipt(command.command_id)
  if (existingReceipt !== null) {
    if (!receiptInputMatches(existingReceipt, {
      command_id: command.command_id,
      case_id: caseValue.case_id,
      contract_version: LOCAL_EXECUTION_CONTRACT,
      input_case_hash: inputCaseHash,
    })) {
      throw new Error('MD_WEB_COMMAND_ID_CONFLICT')
    }
    const persisted = await repository.get(caseValue.case_id)
    if (persisted === null) throw new Error('MD_WEB_CASE_NOT_FOUND')
    return persisted
  }

  const output = apply_command(
    structuredClone(caseValue) as unknown as Record<string, unknown>,
    structuredClone(command) as unknown as Record<string, unknown>,
  ) as CaseV2
  const outputCaseHash = await canonicalSha256(output)
  const receipt: ExecutionReceipt = {
    command_id: command.command_id,
    case_id: caseValue.case_id,
    contract_version: LOCAL_EXECUTION_CONTRACT,
    input_case_hash: inputCaseHash,
    output_case_hash: outputCaseHash,
    applied_at: command.now,
  }
  return await repository.applyWithReceipt(output, receipt)
}

export function buildLocalChecklistProposal(caseValue: CaseV2, mode: 'reconstruction' | 'search'): ProposalModel {
  return build_checklist_proposal_json(
    structuredClone(caseValue) as unknown as Record<string, unknown>,
    mode,
  ) as ProposalModel
}
