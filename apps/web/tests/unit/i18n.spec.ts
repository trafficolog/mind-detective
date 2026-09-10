import { describe, expect, it } from 'vitest'
import { copyKeys, resolveLocale, translate } from '../../app/lib/i18n'

describe('RU/EN copy contract', () => {
  it('keeps exact key parity', () => {
    expect(copyKeys('ru')).toEqual(copyKeys('en'))
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
