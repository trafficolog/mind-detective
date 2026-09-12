import { describe, expect, it } from 'vitest'
import type { CaseV2 } from '../../app/lib/api/contracts'
import { exportCase, importCase } from '../../app/lib/storage/exportImport'

function jsonFile(payload: unknown): File {
  return {
    text: async () => JSON.stringify(payload),
  } as File
}

function blobFile(blob: Blob): File {
  return {
    text: async () => await blob.text(),
  } as File
}

const legacyV1 = {
  schema: 'mind-detective-case/v1',
  case_id: 'legacy-unit',
  item_label: 'паспорт',
  created_at: '2026-09-09T18:00:00Z',
  updated_at: '2026-09-09T18:05:00Z',
  lifecycle: 'active',
  statements: [],
  timeline: null,
  search_checks: [],
  candidates: [],
  next_action: null,
  constraints: [],
  outcome: null,
}

const reconstructionCase: CaseV2 = {
  schema: 'mind-detective-case/v2',
  case_id: 'reconstruction-round-trip',
  item_label: 'ключи',
  created_at: '2026-09-12T17:00:00+03:00',
  updated_at: '2026-09-12T17:30:00+03:00',
  lifecycle: 'active',
  statements: [
    {
      id: 'stmt-1',
      source: 'user',
      statement_type: 'recollection',
      original_text: 'В 17:20 ключи были у меня в руке',
      recorded_at: '2026-09-12T17:26:00+03:00',
      event_time: '2026-09-12T17:20:00+03:00',
      user_confirmation: true,
      supporting_evidence_ids: [],
      limitations: [],
    },
    {
      id: 'stmt-2',
      source: 'user',
      statement_type: 'habit',
      original_text: 'Обычно я кладу ключи на полку у двери',
      recorded_at: '2026-09-12T17:27:00+03:00',
      event_time: null,
      user_confirmation: true,
      supporting_evidence_ids: [],
      limitations: ['это привычка, а не воспоминание об этом эпизоде'],
    },
    {
      id: 'stmt-3',
      source: 'user',
      statement_type: 'observation',
      original_text: 'Позже я заметил, что ключей нет',
      recorded_at: '2026-09-12T17:28:00+03:00',
      event_time: null,
      user_confirmation: true,
      supporting_evidence_ids: [],
      limitations: ['точное время неизвестно'],
    },
  ],
  timeline: {
    last_supported_interaction_id: 'stmt-1',
    first_noticed_missing_id: 'stmt-3',
    events: [
      {
        id: 'event-1',
        label: 'Последний подтверждённый контакт',
        statement_ids: ['stmt-1'],
        event_time: '2026-09-12T17:20:00+03:00',
        time_precision: 'approximate',
      },
    ],
    unknown_intervals: ['точное время неизвестно'],
    contradictions: ['MD_TIME_REFERENCE_MISSING'],
  },
  search_checks: [],
  candidates: [],
  next_action: null,
  constraints: [],
  outcome: null,
  current_mode: 'reconstruction',
  interaction_journal: [
    {
      id: 'free-1',
      author: 'user',
      mode: 'reconstruction',
      entry_type: 'free_account',
      text: 'Я пришёл домой, снял куртку и положил ключи, но не помню куда.',
      created_at: '2026-09-12T17:25:00+03:00',
      statement_ids: [],
      search_check_ids: [],
    },
  ],
  action_feedback: [],
}

describe('local Case import', () => {
  it('migrates legacy v1 to canonical v2 without a validation callback', async () => {
    const imported = await importCase(jsonFile(legacyV1))

    expect(imported).toMatchObject({
      schema: 'mind-detective-case/v2',
      case_id: 'legacy-unit',
      current_mode: 'unselected',
      interaction_journal: [],
      action_feedback: [],
    })
  })

  it('rejects unsupported future schema locally', async () => {
    await expect(importCase(jsonFile({ schema: 'mind-detective-case/v999' })))
      .rejects.toThrow('MD_WEB_IMPORT_SCHEMA')
  })

  it('round-trips reconstruction evidence and derived timeline through Case v2 export/import', async () => {
    const exported = exportCase(reconstructionCase)
    const imported = await importCase(blobFile(exported))

    expect(imported).toEqual(reconstructionCase)
    expect(imported.current_mode).toBe('reconstruction')
    expect(imported.interaction_journal[0]?.entry_type).toBe('free_account')
    expect(imported.timeline?.unknown_intervals).toEqual(reconstructionCase.timeline?.unknown_intervals)
    expect(imported.timeline?.contradictions).toEqual(reconstructionCase.timeline?.contradictions)
  })
})
