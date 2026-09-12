import { describe, expect, it } from 'vitest'
import { copyKeys, resolveLocale, translate } from '../../app/lib/i18n'

describe('RU/EN copy contract', () => {
  it('keeps exact key parity', () => {
    expect(copyKeys('ru')).toEqual(copyKeys('en'))
  })


it('keeps the complete reconstruction copy contract and epistemic boundary', () => {
  const required = [
    'reconstruction.title',
    'reconstruction.free_account.title',
    'reconstruction.free_account.prompt',
    'reconstruction.free_account.submit',
    'reconstruction.free_account.saved',
    'reconstruction.statement.title',
    'reconstruction.statement.type',
    'reconstruction.statement.text',
    'reconstruction.statement.event_time',
    'reconstruction.statement.unknown_time',
    'reconstruction.timeline.title',
    'reconstruction.timeline.rebuild',
    'reconstruction.timeline.unknowns',
    'reconstruction.timeline.contradictions',
    'reconstruction.to_search',
    'reconstruction.mode_label',
  ]
  for (const key of required) {
    expect(copyKeys('ru')).toContain(key)
    expect(copyKeys('en')).toContain(key)
  }
  expect(translate('ru', 'reconstruction.scope')).toContain('не устанавливает')
  expect(translate('en', 'reconstruction.scope').toLowerCase()).toContain('does not establish')
})

  it('preserves required safety and provider-processing semantics in both locales', () => {
    expect(translate('ru', 'guard.banner')).toContain('проверку')
    expect(translate('en', 'guard.banner').toLowerCase()).toContain('safety')
    expect(translate('ru', 'privacy.assistant_provider')).toContain('модельным провайдером')
    expect(translate('en', 'privacy.assistant_provider').toLowerCase()).toContain('model provider')
    expect(translate('ru', 'storage.base')).toContain('Облачной резервной копии')
    expect(translate('en', 'storage.base').toLowerCase()).toContain('no cloud backup')
  })

  it('resolves explicit locale before browser locale', () => {
    expect(resolveLocale('ru', 'en-US')).toBe('ru')
    expect(resolveLocale('en', 'ru-RU')).toBe('en')
    expect(resolveLocale('auto', 'ru-RU')).toBe('ru')
    expect(resolveLocale('auto', 'nl-NL')).toBe('en')
  })

  it('interpolates reviewed template values', () => {
    expect(translate('en', 'quality.title', { target: 'backpack' })).toContain('backpack')
    expect(translate('ru', 'outcome.found', { item: 'ключи' })).toContain('ключи')
  })
})
