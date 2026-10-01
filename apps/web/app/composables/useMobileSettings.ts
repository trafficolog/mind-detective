import { loadSettings, saveSettings, type MobileSettings } from '~/lib/mobile/settings'

function storage(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.localStorage
  } catch {
    return null
  }
}

export function useMobileSettings() {
  const settings = useState<MobileSettings>('md-mobile-settings', () => {
    const store = storage()
    return store ? loadSettings(store) : { onboarded: false, assistantOn: false, server: { url: '', token: '' } }
  })

  function update(patch: Partial<MobileSettings>): void {
    settings.value = { ...settings.value, ...patch, server: { ...settings.value.server, ...(patch.server ?? {}) } }
    const store = storage()
    if (store) saveSettings(store, settings.value)
  }

  return { settings, update }
}
