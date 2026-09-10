import { computed, type ComputedRef } from 'vue'
import { resolveLocale, translate, type CopyKey, type Locale } from '~/lib/i18n'

export interface CopyApi {
  locale: ComputedRef<Locale>
  t(key: CopyKey, values?: Record<string, string | number>): string
}

export function useCopy(): CopyApi {
  const config = useRuntimeConfig()
  const locale = computed<Locale>(() => {
    const browserLanguage = import.meta.client ? navigator.language : ''
    return resolveLocale(String(config.public.mindDetectiveLocale || 'auto'), browserLanguage)
  })
  return {
    locale,
    t: (key, values) => translate(locale.value, key, values),
  }
}
