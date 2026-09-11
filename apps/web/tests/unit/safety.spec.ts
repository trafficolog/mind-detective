import { describe, expect, it } from 'vitest'
import { classifySafetyInput, safetyCodeForInput } from '../../app/lib/safety'

describe('browser safety ingress', () => {
  it.each([
    ['Принимал ли я таблетки?', 'MD_SAFE_MEDICATION_ACTION'],
    ['Я выключил плиту перед уходом?', 'MD_SAFE_HAZARDOUS_ACTION'],
    ['Я закрыл входную дверь?', 'MD_SAFE_SECURITY_ACTION'],
    ['Did I already take the medicine?', 'MD_SAFE_MEDICATION_ACTION'],
    ['Did I turn off the stove?', 'MD_SAFE_HAZARDOUS_ACTION'],
    ['Did I lock the door?', 'MD_SAFE_SECURITY_ACTION'],
  ])('routes %s outside lost-item search', (text, code) => {
    const decision = classifySafetyInput(text)
    expect(decision.route).toBe('limit_and_escalate')
    expect(decision.codes).toContain(code)
    expect(safetyCodeForInput(text)).toBe(code)
  })

  it.each([
    'коробка с таблетками',
    'ключи от входной двери',
    'пульт рядом с плитой',
    'medicine box',
  ])('keeps ordinary lost-item text searchable: %s', (text) => {
    expect(classifySafetyInput(text)).toEqual({
      route: 'ordinary_search',
      codes: [],
      messageKey: 'ordinary_lost_item_search',
    })
    expect(safetyCodeForInput(text)).toBeNull()
  })
})
