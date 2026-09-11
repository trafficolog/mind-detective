import { describe, expect, it } from 'vitest'
import type { CaseV2, CommandEnvelope } from '../../app/lib/api/contracts'
import { captureRetryableCommand, cloneRetryableCommand } from '../../app/lib/execution/retryState'

function caseFixture(): CaseV2 {
  return {
    schema: 'mind-detective-case/v2',
    case_id: 'case-retry',
    item_label: 'ключи',
    created_at: '2026-09-11T18:00:00Z',
    updated_at: '2026-09-11T18:00:00Z',
    lifecycle: 'active',
    statements: [],
    timeline: null,
    search_checks: [],
    candidates: [],
    next_action: null,
    constraints: [],
    outcome: null,
    current_mode: 'search',
    interaction_journal: [],
    action_feedback: [],
  }
}

function commandFixture(): CommandEnvelope {
  return {
    command_id: 'cmd-retry',
    expected_updated_at: '2026-09-11T18:00:00Z',
    command_type: 'pause',
    now: '2026-09-11T18:01:00Z',
    payload: {},
  }
}

describe('local persistence retry state', () => {
  it('retries byte-equivalent case snapshot and envelope after failure', () => {
    const sourceCase = caseFixture()
    const sourceCommand = commandFixture()
    const captured = captureRetryableCommand(sourceCase, sourceCommand)

    sourceCase.item_label = 'mutated outside retry state'
    sourceCommand.command_id = 'mutated-command'

    const retry = cloneRetryableCommand(captured)
    expect(retry.caseSnapshot.item_label).toBe('ключи')
    expect(retry.command).toEqual(commandFixture())
    expect(JSON.stringify(retry)).toBe(JSON.stringify(captured))

    retry.caseSnapshot.item_label = 'mutated retry clone'
    retry.command.payload.extra = true
    expect(captured.caseSnapshot.item_label).toBe('ключи')
    expect(captured.command.payload).toEqual({})
  })
})
