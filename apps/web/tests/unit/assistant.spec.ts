import { describe, expect, it } from 'vitest'
import { assistantContext, assistantPrompt, fallbackProposal, guardProposal, proposalFlow, ProposalRejected } from '../../app/lib/assistant/proposals'
import { CaseBuilder } from './support/mobileCases'

function sc(): CaseBuilder {
  return CaseBuilder.create('Ключи').search()
    .freeAccount('секретный рассказ')
    .statement('recollection', 'Ключи в руке')
    .statement('hypothesis', 'Может, в машине')
    .target('A').target('B')
}

function rejected(fn: () => unknown): boolean {
  try { fn() } catch (error) { return error instanceof ProposalRejected }
  return false
}

describe('research-only assistant boundary (ADR 017)', () => {
  it('T22 minimal context excludes the free account and hypotheses', () => {
    const context = assistantContext(sc().value)
    expect(JSON.stringify(context).includes('секретный')).toBe(false)
    expect(JSON.stringify(context).includes('Может, в машине')).toBe(false)
    expect(context.confirmed).toEqual(['Ключи в руке'])
    expect(context.zones).toEqual([{ name: 'A', state: 'Не проверено' }, { name: 'B', state: 'Не проверено' }])
    expect(context).toMatchObject({ item: 'Ключи', kind: 'physical', mode: 'search' })
  })

  it('T23 guard extracts JSON from model text', () => {
    const p = guardProposal('Вот: ```json {"kind":"check","text":"Проверьте карман пальто","place":"Карман пальто"} ```', sc().value)
    expect(p).toEqual({ kind: 'check', text: 'Проверьте карман пальто', place: 'Карман пальто' })
  })

  it('T24 guard rejects probabilities and percentages', () => {
    expect(rejected(() => guardProposal('{"kind":"check","text":"Вероятнее всего в машине","place":"Машина"}', sc().value))).toBe(true)
    expect(rejected(() => guardProposal('{"kind":"question","text":"С точностью 92% это дома?"}', sc().value))).toBe(true)
    expect(rejected(() => guardProposal('no json at all', sc().value))).toBe(true)
  })

  it('T25 guard rejects re-checking a checked place and checks outside Search', () => {
    const checked = sc().check('A', 'hand').value
    expect(rejected(() => guardProposal('{"kind":"check","text":"Проверьте A ещё раз","place":"A"}', checked))).toBe(true)
    const recon = CaseBuilder.create().reconstruction().value
    expect(rejected(() => guardProposal('{"kind":"check","text":"Проверьте шкаф","place":"Шкаф"}', recon))).toBe(true)
    expect(guardProposal('{"kind":"question","text":"Что было после кафе?"}', recon)).toEqual({ kind: 'question', text: 'Что было после кафе?' })
  })

  it('T26 search fallback proposes the first unchecked place', () => {
    expect(fallbackProposal(sc().value)).toEqual({ kind: 'check', place: 'A', text: 'Проверьте: A' })
    expect(fallbackProposal(CaseBuilder.create().search().value)).toEqual({
      kind: 'question', text: 'Есть ли место, которое вы ещё не называли? Добавьте его в список сами.',
    })
  })

  it('T27 reconstruction fallback asks about the unknown event', () => {
    const c = CaseBuilder.create().reconstruction().freeAccount().events([['Дорога', 'unknown', null]]).value
    expect(fallbackProposal(c).text).toBe('Что вы помните о событии «Дорога»?')
    expect(fallbackProposal(CaseBuilder.create().reconstruction().value).text).toBe('Что вы помните о последнем моменте, когда видели вещь?')
  })

  it('T28 network error falls back as unavailable', async () => {
    const p = await proposalFlow(sc().value, async () => { throw new Error('net') })
    expect([p.source, p.reason]).toEqual(['fallback', 'unavailable'])
  })

  it('T29 rejected model answer falls back as rejected', async () => {
    const p = await proposalFlow(sc().value, async () => '{"kind":"check","text":"Скорее всего в кармане","place":"Карман"}')
    expect([p.source, p.reason]).toEqual(['fallback', 'rejected'])
  })

  it('T30 valid answer is labelled as assistant', async () => {
    const p = await proposalFlow(sc().value, async () => '{"kind":"check","text":"Проверьте карман пальто","place":"Карман пальто"}')
    expect(p).toEqual({ kind: 'check', text: 'Проверьте карман пальто', place: 'Карман пальто', source: 'assistant' })
  })

  it('T31 timeout falls back', async () => {
    const p = await proposalFlow(sc().value, () => new Promise<string>(() => {}), 20)
    expect(p.source).toBe('fallback')
  })

  it('T40 digital case: prompt and fallback about sources without file access', () => {
    const digital = CaseBuilder.create('Фото', 'digital').search().value
    expect(fallbackProposal(digital).text.includes('устройство')).toBe(true)
    expect(assistantPrompt(digital).includes('Не проси доступ к файлам')).toBe(true)
    expect(assistantPrompt(sc().value).includes('секретный')).toBe(false)
  })
})
