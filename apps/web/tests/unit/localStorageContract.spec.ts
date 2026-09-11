import { describe, expect, it } from 'vitest'
import type { CaseV2 } from '../../app/lib/api/contracts'
import {
  DB_VERSION,
  EXECUTION_RECEIPT_STORE,
  createIdentityMatches,
  receiptInputMatches,
  type ExecutionReceipt,
} from '../../app/lib/storage/indexeddb'

const baseCase: CaseV2 = {
  schema: 'mind-detective-case/v2',
  case_id: 'case-storage',
  item_label: 'ключи',
  created_at: '2026-09-10T18:00:00Z',
  updated_at: '2026-09-10T18:00:00Z',
  lifecycle: 'active',
  statements: [],
  timeline: null,
  search_checks: [],
  candidates: [],
  next_action: null,
  constraints: [],
  outcome: null,
  current_mode: 'unselected',
  interaction_journal: [],
  action_feedback: [],
}

const receipt: ExecutionReceipt = {
  command_id: 'cmd-1',
  case_id: baseCase.case_id,
  contract_version: 'mind-detective-local-execution/v1',
  input_case_hash: 'sha256:input',
  output_case_hash: 'sha256:output',
  applied_at: '2026-09-10T18:01:00Z',
}

describe('local execution storage contract', () => {
  it('uses IndexedDB v2 with a dedicated receipt store', () => {
    expect(DB_VERSION).toBe(2)
    expect(EXECUTION_RECEIPT_STORE).toBe('execution_receipts')
  })

  it('matches create identity by case id item label and created_at only', () => {
    expect(createIdentityMatches(baseCase, structuredClone(baseCase))).toBe(true)
    expect(createIdentityMatches(baseCase, { ...baseCase, updated_at: '2026-09-10T19:00:00Z' })).toBe(true)
    expect(createIdentityMatches(baseCase, { ...baseCase, item_label: 'телефон' })).toBe(false)
  })

  it('matches a receipt only for the same command case contract and input hash', () => {
    expect(receiptInputMatches(receipt, {
      command_id: 'cmd-1',
      case_id: 'case-storage',
      contract_version: 'mind-detective-local-execution/v1',
      input_case_hash: 'sha256:input',
    })).toBe(true)
    expect(receiptInputMatches(receipt, {
      command_id: 'cmd-1',
      case_id: 'case-storage',
      contract_version: 'mind-detective-local-execution/v1',
      input_case_hash: 'sha256:different',
    })).toBe(false)
  })
})
