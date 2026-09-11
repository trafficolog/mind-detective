import { describe, expect, it } from 'vitest'
import {
  EVALUATION_ASSIGNMENT_VERSION,
  EVALUATION_EXPORT_SCHEMA,
  EVALUATION_SCHEMA,
  type EvaluationExportV1,
} from '../../app/lib/eval/contracts'
import { appendEvalEvent, exportEvalCsv, exportEvalJson, type EvalEvent } from '../../app/lib/eval/log'

describe('local evaluation log privacy contract', () => {
  it('rejects sensitive evaluation keys synchronously on the legacy compatibility path', () => {
    expect(() => appendEvalEvent('found', { item_label: 'ключи' })).toThrow('sensitive evaluation field: item_label')
    expect(() => appendEvalEvent('next_action_shown', { target: 'рюкзак' })).toThrow('sensitive evaluation field: target')
    expect(() => appendEvalEvent('ai_guard_blocked', { raw_model_output: 'secret' })).toThrow('sensitive evaluation field: raw_model_output')
  })

  it('rejects metadata outside the explicit legacy allowlist', () => {
    expect(() => appendEvalEvent('found', { custom_note: 'text' })).toThrow('unexpected evaluation field: custom_note')
  })

  it('keeps legacy export helpers privacy-filtered during migration', async () => {
    const event: EvalEvent = {
      event_id: 'event-1',
      event: 'found_context_recorded',
      at: '2026-09-10T07:00:00Z',
      metadata: { case_id: 'case-1', found_context: 'elsewhere_unplanned' },
    }
    const json = await exportEvalJson([event]).text()
    const csv = await exportEvalCsv([event]).text()
    expect(json).toContain('elsewhere_unplanned')
    expect(csv).toContain('found_context_recorded')
    expect(json).not.toContain('item_label')
    expect(csv).not.toContain('target')
  })

  it('exports the v1 bundle without Case or free-text fields', async () => {
    const bundle: EvaluationExportV1 = {
      export_schema: EVALUATION_EXPORT_SCHEMA,
      exported_at: '2026-09-11T08:10:00Z',
      participants: [{
        evaluation_schema: EVALUATION_SCHEMA,
        participant_id: 'participant-1',
        protocol: 'staged',
        enrollment_slot: 1,
        counterbalance_cell: 1,
        created_at: '2026-09-11T08:00:00Z',
      }],
      sessions: [{
        evaluation_schema: EVALUATION_SCHEMA,
        evaluation_session_id: 'session-1',
        participant_id: 'participant-1',
        protocol: 'staged',
        arm: 'B',
        assignment_version: EVALUATION_ASSIGNMENT_VERSION,
        counterbalance_cell: 1,
        scenario_family: 'S1',
        scenario_variant: 'A',
        order_position: 1,
        case_id: 'case-1',
        started_at: '2026-09-11T08:00:00Z',
        ended_at: '2026-09-11T08:02:00Z',
        outcome: 'found',
      }],
      events: [{
        event_id: 'event-2',
        evaluation_session_id: 'session-1',
        event: 'case_started',
        at: '2026-09-11T08:00:00Z',
        metadata: { case_id: 'case-1' },
      }],
    }

    const json = await exportEvalJson(bundle).text()
    const csv = await exportEvalCsv(bundle).text()
    expect(json).toContain(EVALUATION_EXPORT_SCHEMA)
    expect(csv).toContain('record_type')
    expect(csv).toContain('participant')
    expect(csv).toContain('session')
    expect(csv).toContain('event')
    expect(json).not.toContain('item_label')
    expect(json).not.toContain('journal_text')
    expect(json).not.toContain('raw_model_output')
  })
})
