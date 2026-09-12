import { describe, expect, it } from 'vitest'
import { importCase } from '../../app/lib/storage/exportImport'

function jsonFile(payload: unknown): File {
  return {
    text: async () => JSON.stringify(payload),
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
})
