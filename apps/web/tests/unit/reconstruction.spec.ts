import { describe, expect, it } from 'vitest'
import type { CaseV2, JournalEntryV2, TimelineEventV2 } from '../../app/lib/api/contracts'
import {
  buildRebuildTimelinePayload,
  buildRecordFreeAccountPayload,
  freeAccountText,
  hasFreeAccount,
} from '../../app/composables/useReconstruction'

function baseCase(interactionJournal: JournalEntryV2[] = []): CaseV2 {
  return {
    schema: 'mind-detective-case/v2',
    case_id: 'case-reconstruction',
    item_label: 'ключи',
    created_at: '2026-09-12T18:00:00Z',
    updated_at: '2026-09-12T18:00:00Z',
    lifecycle: 'active',
    statements: [],
    timeline: null,
    search_checks: [],
    candidates: [],
    next_action: null,
    constraints: [],
    outcome: null,
    current_mode: 'reconstruction',
    interaction_journal: interactionJournal,
    action_feedback: [],
  }
}

function journalEntry(overrides: Partial<JournalEntryV2> = {}): JournalEntryV2 {
  return {
    id: 'journal-1',
    author: 'user',
    mode: 'reconstruction',
    entry_type: 'free_account',
    text: 'Я положил ключи, но не помню куда.',
    created_at: '2026-09-12T18:01:00Z',
    statement_ids: [],
    search_check_ids: [],
    ...overrides,
  }
}

describe('reconstruction view helpers', () => {
  it('recognizes only the canonical user reconstruction free-account entry', () => {
    expect(hasFreeAccount(baseCase())).toBe(false)
    expect(hasFreeAccount(baseCase([journalEntry({ author: 'assistant' })]))).toBe(false)
    expect(hasFreeAccount(baseCase([journalEntry({ mode: 'search' })]))).toBe(false)
    expect(hasFreeAccount(baseCase([journalEntry({ entry_type: 'note' })]))).toBe(false)
    expect(hasFreeAccount(baseCase([journalEntry()]))).toBe(true)
  })

  it('returns the canonical free account verbatim and ignores lookalike entries', () => {
    const verbatim = '  Сначала ключи были у меня.\nПотом я отвлёкся.  '
    const caseValue = baseCase([
      journalEntry({ id: 'assistant-free', author: 'assistant', text: 'не использовать' }),
      journalEntry({ id: 'search-free', mode: 'search', text: 'не использовать' }),
      journalEntry({ id: 'free-1', text: verbatim }),
    ])

    expect(freeAccountText(caseValue)).toBe(verbatim)
    expect(freeAccountText(baseCase())).toBeNull()
  })

  it('builds the record-free-account payload without normalizing user text', () => {
    const text = '  Я вернулся домой и положил ключи.  '

    expect(buildRecordFreeAccountPayload('free-1', text)).toEqual({
      entry_id: 'free-1',
      text,
    })
  })

  it('builds only canonical timeline input and never derives unknowns or contradictions', () => {
    const events: TimelineEventV2[] = [
      {
        id: 'event-1',
        label: 'Последний подтверждённый контакт',
        statement_ids: ['stmt-1'],
        event_time: '2026-09-12T17:40:00Z',
        time_precision: 'approximate',
      },
    ]

    const payload = buildRebuildTimelinePayload(events, 'stmt-1', null)

    expect(payload).toEqual({
      events,
      last_supported_interaction_id: 'stmt-1',
      first_noticed_missing_id: null,
    })
    expect(Object.keys(payload).sort()).toEqual([
      'events',
      'first_noticed_missing_id',
      'last_supported_interaction_id',
    ])
    expect(payload).not.toHaveProperty('unknown_intervals')
    expect(payload).not.toHaveProperty('contradictions')
  })
})
