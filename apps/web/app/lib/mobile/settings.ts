// Per-browser conveniences for the mobile shell. Canonical Case data never lives here (ADR 010).
export interface ServerConfig {
  url: string
  token: string
}

export interface MobileSettings {
  onboarded: boolean
  assistantOn: boolean
  server: ServerConfig
}

export const SETTINGS_KEYS = {
  onboarded: 'md.mobile.onboarded',
  assistant: 'md.mobile.assistant',
  server: 'md.mobile.server',
} as const

function read(storage: Storage, key: string): string | null {
  try {
    return storage.getItem(key)
  } catch {
    return null
  }
}

function write(storage: Storage, key: string, value: string): void {
  try {
    storage.setItem(key, value)
  } catch {
    // Storage may be unavailable (private mode); settings then last for the session only.
  }
}

function parseServer(raw: string | null): ServerConfig {
  if (!raw) return { url: '', token: '' }
  try {
    const value = JSON.parse(raw) as Partial<ServerConfig>
    return {
      url: typeof value.url === 'string' ? value.url : '',
      token: typeof value.token === 'string' ? value.token : '',
    }
  } catch {
    return { url: '', token: '' }
  }
}

export function loadSettings(storage: Storage): MobileSettings {
  return {
    onboarded: read(storage, SETTINGS_KEYS.onboarded) === '1',
    assistantOn: read(storage, SETTINGS_KEYS.assistant) === '1',
    server: parseServer(read(storage, SETTINGS_KEYS.server)),
  }
}

export function saveSettings(storage: Storage, settings: MobileSettings): void {
  write(storage, SETTINGS_KEYS.onboarded, settings.onboarded ? '1' : '0')
  write(storage, SETTINGS_KEYS.assistant, settings.assistantOn ? '1' : '0')
  write(storage, SETTINGS_KEYS.server, JSON.stringify(settings.server))
}
