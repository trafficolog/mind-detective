import { describe, expect, it } from 'vitest'
import type { CaseV2, CommandEnvelope } from '../../app/lib/api/contracts'
import {
  applyLocalCommand,
  createLocalCase,
  createLocalSearchCase,
  type LocalExecutionRepository,
} from '../../app/lib/execution/localExecutor'
import type { ExecutionReceipt } from '../../app/lib/storage/indexeddb'

function baseCase(): CaseV2 {
  return {
    schema: 'mind-detective-case/v2',
    case_id: 'case-local',
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
}

class MemoryRepository implements LocalExecutionRepository {
  cases = new Map<string, CaseV2>()
  receipts = new Map<string, ExecutionReceipt>()
  writes = 0
  createWrites = 0

  async get(caseId: string): Promise<CaseV2 | null> {
    return this.cases.get(caseId) ?? null
  }

  async createOnly(caseValue: CaseV2): Promise<CaseV2> {
    const existing = this.cases.get(caseValue.case_id)
    if (existing) {
      if (existing.item_label !== caseValue.item_label || existing.created_at !== caseValue.created_at) {
        throw new Error('MD_WEB_CASE_ID_CONFLICT')
      }
      return existing
    }
    this.createWrites += 1
    this.cases.set(caseValue.case_id, structuredClone(caseValue))
    return caseValue
  }

  async getReceipt(commandId: string): Promise<ExecutionReceipt | null> {
    return this.receipts.get(commandId) ?? null
  }

  async applyWithReceipt(caseValue: CaseV2, receipt: ExecutionReceipt): Promise<CaseV2> {
    this.writes += 1
    this.cases.set(caseValue.case_id, structuredClone(caseValue))
    this.receipts.set(receipt.command_id, structuredClone(receipt))
    return caseValue
  }
}

const modeCommand: CommandEnvelope = {
  command_id: 'cmd-mode-1',
  expected_updated_at: '2026-09-10T18:00:00Z',
  command_type: 'set_mode',
  now: '2026-09-10T18:01:00Z',
  payload: { mode: 'search' },
}

describe('local executor wrapper', () => {
  it('applies a deterministic command once and reuses matching receipt on retry', async () => {
    const repository = new MemoryRepository()
    const source = baseCase()
    repository.cases.set(source.case_id, structuredClone(source))

    const first = await applyLocalCommand(repository, source, modeCommand)
    const second = await applyLocalCommand(repository, source, modeCommand)

    expect(first.current_mode).toBe('search')
    expect(second).toEqual(first)
    expect(repository.writes).toBe(1)
    expect(repository.receipts.size).toBe(1)
  })

  it('fails closed when a command id is reused with another input case', async () => {
    const repository = new MemoryRepository()
    const source = baseCase()
    repository.cases.set(source.case_id, structuredClone(source))
    await applyLocalCommand(repository, source, modeCommand)

    const conflicting = { ...source, updated_at: '2026-09-10T17:59:00Z' }
    await expect(applyLocalCommand(repository, conflicting, modeCommand))
      .rejects.toThrow('MD_WEB_COMMAND_ID_CONFLICT')
    expect(repository.writes).toBe(1)
  })

  it('creates a case locally with create-only conflict protection', async () => {
    const repository = new MemoryRepository()
    const first = await createLocalCase(repository, 'case-new', 'паспорт', '2026-09-10T18:00:00Z')
    const retry = await createLocalCase(repository, 'case-new', 'паспорт', '2026-09-10T18:00:00Z')
    expect(retry).toEqual(first)
    await expect(createLocalCase(repository, 'case-new', 'телефон', '2026-09-10T18:00:00Z'))
      .rejects.toThrow('MD_WEB_CASE_ID_CONFLICT')
  })

  it('creates the Web search case before the single create-only persistence write', async () => {
    const repository = new MemoryRepository()
    const created = await createLocalSearchCase(repository, 'case-search', 'паспорт', '2026-09-10T18:00:00Z')

    expect(created.current_mode).toBe('search')
    expect(repository.cases.get('case-search')?.current_mode).toBe('search')
    expect(repository.createWrites).toBe(1)
    expect(repository.writes).toBe(0)
    expect(repository.receipts.size).toBe(0)
  })

  it('runs reconstruction commands through the existing generic receipt boundary', async () => {
    const repository = new MemoryRepository()
    const source = baseCase()
    repository.cases.set(source.case_id, structuredClone(source))

    const reconstruction = await applyLocalCommand(repository, source, {
      command_id: 'cmd-reconstruction-mode',
      expected_updated_at: source.updated_at,
      command_type: 'set_mode',
      now: '2026-09-10T18:01:00Z',
      payload: { mode: 'reconstruction' },
    })

    const withFreeAccount = await applyLocalCommand(repository, reconstruction, {
      command_id: 'cmd-free-account',
      expected_updated_at: reconstruction.updated_at,
      command_type: 'record_free_account',
      now: '2026-09-10T18:02:00Z',
      payload: {
        entry_id: 'free-1',
        text: 'Я пришёл домой и положил ключи, но не помню куда.',
      },
    })

    const withTimeline = await applyLocalCommand(repository, withFreeAccount, {
      command_id: 'cmd-rebuild-timeline',
      expected_updated_at: withFreeAccount.updated_at,
      command_type: 'rebuild_timeline',
      now: '2026-09-10T18:03:00Z',
      payload: {
        events: [],
        last_supported_interaction_id: null,
        first_noticed_missing_id: null,
      },
    })

    expect(withFreeAccount.interaction_journal).toHaveLength(1)
    expect(withFreeAccount.interaction_journal[0]?.entry_type).toBe('free_account')
    expect(withTimeline.timeline?.events).toEqual([])
    expect(repository.writes).toBe(3)
    expect(repository.receipts.size).toBe(3)
  })
})
