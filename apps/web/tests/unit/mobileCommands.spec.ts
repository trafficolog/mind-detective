import { describe, expect, it } from 'vitest'
import {
  afterCheckCommand, checkCommand, closeCommand, errorMessage, eventCommand, freeAccountCommand, MobileInputError,
  pauseToggleCommand, setModeCommand, statementCommand, targetCommand,
} from '../../app/lib/mobile/commands'
import { apply_command } from '../../app/generated/localExecution'
import type { CaseV2, CommandEnvelope } from '../../app/lib/api/contracts'
import { CaseBuilder } from './support/mobileCases'

const CTX = { now: '2026-09-30T12:00:00Z', id: 'fixed-id' }

function apply(c: CaseV2, command: CommandEnvelope): CaseV2 {
  return apply_command(structuredClone(c) as unknown as Record<string, unknown>, structuredClone(command) as unknown as Record<string, unknown>) as CaseV2
}

function inputError(fn: () => unknown): string {
  try { fn() } catch (error) { if (error instanceof MobileInputError) return error.code; throw error }
  throw new Error('expected MobileInputError')
}

describe('mobile command envelopes (typed input → portable kernel)', () => {
  it('builds envelopes against the current case version', () => {
    const c = CaseBuilder.create().value
    const cmd = setModeCommand(c, 'search', CTX)
    expect(cmd).toEqual({ command_id: 'fixed-id', expected_updated_at: c.updated_at, command_type: 'set_mode', now: CTX.now, payload: { mode: 'search' } })
  })

  it('T03 records the first free account verbatim and revises afterwards', () => {
    const c = CaseBuilder.create().reconstruction().value
    const first = freeAccountCommand(c, '  ну…  вышел \n', CTX)
    expect(first.command_type).toBe('record_free_account')
    expect(first.payload).toEqual({ entry_id: 'free-account-fixed-id', text: '  ну…  вышел \n' })
    const recorded = apply(c, first)
    const second = freeAccountCommand(recorded, 'другой', { ...CTX, id: 'id-2' })
    expect(second.command_type).toBe('revise_free_account')
    expect(inputError(() => freeAccountCommand(c, '   ', CTX))).toBe('text_required')
  })

  it('T04 T06 validates statements before sending', () => {
    const c = CaseBuilder.create().reconstruction().freeAccount().value
    expect(inputError(() => statementCommand(c, { type: 'recollection', text: ' ' }, CTX))).toBe('text_required')
    expect(inputError(() => statementCommand(c, { type: 'x', text: 'a' }, CTX))).toBe('type_invalid')
    expect(inputError(() => statementCommand(c, { type: 'habit', text: 'a', time: '25:99' }, CTX))).toBe('time_invalid')
    const cmd = statementCommand(c, { type: 'recollection', text: ' Ключи в руке ', time: '8:00', limitation: ' не уверен ' }, CTX)
    expect(cmd.payload).toEqual({
      statement_id: 'statement-fixed-id', source: 'user', statement_type: 'recollection', original_text: 'Ключи в руке',
      event_time: '08:00', user_confirmation: true, supporting_evidence_ids: [], limitations: ['не уверен'],
    })
    expect(apply(c, cmd).statements).toHaveLength(1)
  })

  it('appends events to the existing timeline through rebuild_timeline', () => {
    let c = CaseBuilder.create().reconstruction().freeAccount().value
    c = apply(c, eventCommand(c, { title: 'Офис', precision: 'exact', time: '08:00' }, { ...CTX, id: 'a' }))
    c = apply(c, eventCommand(c, { title: 'Дорога', precision: 'unknown', time: '12:00' }, { ...CTX, id: 'b', now: '2026-09-30T12:01:00Z' }))
    expect(c.timeline?.events.map(e => [e.id, e.label, e.event_time, e.time_precision])).toEqual([
      ['event-a', 'Офис', '08:00', 'exact'], ['event-b', 'Дорога', null, 'unknown'],
    ])
    expect(inputError(() => eventCommand(c, { title: ' ', precision: 'exact', time: '08:00' }, CTX))).toBe('title_required')
    expect(inputError(() => eventCommand(c, { title: 'A', precision: 'exact', time: '25:99' }, CTX))).toBe('time_invalid')
    expect(inputError(() => eventCommand(c, { title: 'A', precision: 'x', time: '' }, CTX))).toBe('precision_invalid')
  })

  it('links a check to the matching place and T15 closes the case after a found check', () => {
    let c = CaseBuilder.create().search().target('Рюкзак').value
    expect(inputError(() => targetCommand(c, '  ', CTX))).toBe('title_required')
    expect(inputError(() => checkCommand(c, { place: ' ', method: 'hand', result: 'not_found' }, CTX))).toBe('place_required')
    const check = checkCommand(c, { place: 'рюкзак', method: 'hand', result: 'found', note: ' в кармане ' }, CTX)
    expect(check.payload).toMatchObject({ target: 'рюкзак', method: 'hand', result: 'found', based_on: [c.candidates[0]!.id], notes: ['в кармане'] })
    c = apply(c, check)
    const close = afterCheckCommand(c, 'found', { ...CTX, id: 'close', now: '2026-09-30T12:01:00Z' })
    expect(close?.command_type).toBe('close_found')
    c = apply(c, close!)
    expect(c.lifecycle).toBe('closed_found')
    expect(afterCheckCommand(c, 'not_found', CTX)).toBeNull()
  })

  it('maps close outcomes to canonical found context', () => {
    const c = CaseBuilder.create().search().value
    expect(closeCommand(c, 'found', 'elsewhere', CTX).payload).toEqual({ outcome: { found_context: 'elsewhere_unplanned' } })
    expect(closeCommand(c, 'found', 'current', CTX).payload).toEqual({ outcome: { found_context: 'current_suggested_action' } })
    expect(closeCommand(c, 'found', 'previous', CTX).payload).toEqual({ outcome: { found_context: 'after_previous_check' } })
    expect(closeCommand(c, 'closed', 'unknown', CTX)).toMatchObject({ command_type: 'close_unresolved', payload: { outcome: {} } })
  })

  it('toggles pause and resume', () => {
    const c = CaseBuilder.create().search().value
    expect(pauseToggleCommand(c, CTX).command_type).toBe('pause')
    expect(pauseToggleCommand(apply(c, pauseToggleCommand(c, CTX)), CTX).command_type).toBe('resume')
  })

  it('translates kernel and input codes into calm Russian messages', () => {
    expect(errorMessage('MD_SEARCH_TARGET_EXISTS', 'physical')).toBe('Такое место уже есть в списке.')
    expect(errorMessage('MD_SEARCH_TARGET_EXISTS', 'digital')).toBe('Такой источник уже есть в списке.')
    expect(errorMessage('MD_CASE_TERMINAL', 'physical')).toBe('Дело завершено и не изменяется.')
    expect(errorMessage('time_invalid', 'physical')).toBe('Укажите время в формате ЧЧ:ММ.')
    expect(errorMessage('MD_SEARCH_MODE_REQUIRED', 'digital')).toBe('Сначала перейдите к проверке источников.')
    expect(errorMessage('unexpected', 'physical')).toBe('Не удалось сохранить.')
  })
})
