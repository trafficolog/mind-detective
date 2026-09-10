import { describe, expect, it } from 'vitest'
import { appendEvalEvent, exportEvalCsv, exportEvalJson, type EvalEvent } from '../../app/lib/eval/log'

describe('local evaluation log privacy contract', () => {
  it('rejects sensitive evaluation keys synchronously', () => {
    expect(() => appendEvalEvent('found', { item_label: 'ключи' })).toThrow('sensitive evaluation field: item_label')
    expect(() => appendEvalEvent('next_action_shown', { target: 'рюкзак' })).toThrow('sensitive evaluation field: target')
    expect(() => appendEvalEvent('ai_guard_blocked', { raw_model_output: 'secret' })).toThrow('sensitive evaluation field: raw_model_output')
  })

  it('rejects metadata outside the explicit allowlist', () => {
    expect(() => appendEvalEvent('found', { custom_note: 'text' })).toThrow('unexpected evaluation field: custom_note')
  })

  it('exports only supplied privacy-filtered event records', async () => {
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
})
