import { describe, expect, it } from 'vitest'
import { methodLabel, methodsFor, vocab, STATEMENT_TYPES, PRECISIONS, RESULTS, dsMethodKey } from '../../app/lib/mobile/vocab'

describe('mobile vocabulary (MEANING.md)', () => {
  it('T38 place / source vocabulary depends on item kind', () => {
    expect(vocab('physical').place).toBe('место')
    expect(vocab('digital').place).toBe('источник')
    expect(vocab('physical').places).toBe('Места проверки')
    expect(vocab('digital').places).toBe('Источники проверки')
    expect(vocab('physical').goSearch).toBe('Перейти к физическому поиску')
    expect(vocab('digital').goSearch).toBe('Перейти к проверке источников')
    expect(vocab('physical').found).toBe('Вещь найдена')
    expect(vocab('digital').found).toBe('Файл найден')
    expect(vocab('physical').icon).toBe('key-round')
    expect(vocab('digital').icon).toBe('image')
  })

  it('T37 method sets follow kernel keys per item kind', () => {
    expect(Object.keys(methodsFor('physical'))).toEqual(['visual', 'hand', 'flashlight', 'opened', 'moved', 'asked'])
    expect(Object.keys(methodsFor('digital'))).toEqual(['name_search', 'date_filter', 'browsed', 'trash', 'shared', 'asked'])
    expect(methodLabel('hand')).toBe('Проверил руками')
    expect(methodLabel('trash')).toBe('Проверил «Удалённые» / корзину')
    expect(methodLabel('reported_check')).toBe('Отмечено как проверенное')
  })

  it('maps kernel method keys to design-system SearchCheckCard keys', () => {
    expect(dsMethodKey('name_search')).toBe('name-search')
    expect(dsMethodKey('date_filter')).toBe('date-filter')
    expect(dsMethodKey('hand')).toBe('hand')
    expect(dsMethodKey('tactile')).toBe('hand')
    expect(dsMethodKey('reported_check')).toBe('other')
  })

  it('keeps design labels for statement types, precisions and results', () => {
    expect(STATEMENT_TYPES).toEqual({ recollection: 'Воспоминание', habit: 'Обычная привычка', observation: 'Наблюдение', hypothesis: 'Гипотеза' })
    expect(PRECISIONS).toEqual({ exact: 'Точное', approximate: 'Примерное', unknown: 'Неизвестное' })
    expect(RESULTS).toEqual({ not_found: 'Не нашёл', partial: 'Проверка неполная', found: 'Нашёл' })
  })
})
