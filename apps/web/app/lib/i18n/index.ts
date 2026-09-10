import { en } from './en'
import { ru, type CopyKey } from './ru'

export type Locale = 'ru' | 'en'
export type { CopyKey }

const dictionaries: Record<Locale, Record<CopyKey, string>> = { ru, en }

export function resolveLocale(configured: string, browserLanguage = ''): Locale {
  if (configured === 'ru' || configured === 'en') return configured
  return browserLanguage.toLowerCase().startsWith('ru') ? 'ru' : 'en'
}

export function translate(
  locale: Locale,
  key: CopyKey,
  values: Record<string, string | number> = {},
): string {
  let text = dictionaries[locale][key]
  for (const [name, value] of Object.entries(values)) {
    text = text.replaceAll(`{${name}}`, String(value))
  }
  return text
}

export function copyKeys(locale: Locale): string[] {
  return Object.keys(dictionaries[locale]).sort()
}
