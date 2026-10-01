import { describe, expect, it } from 'vitest'
import { loadSettings, saveSettings, SETTINGS_KEYS } from '../../app/lib/mobile/settings'

function memoryStorage(): Storage {
  const data = new Map<string, string>()
  return {
    get length() { return data.size },
    clear: () => data.clear(),
    getItem: key => data.get(key) ?? null,
    key: index => [...data.keys()][index] ?? null,
    removeItem: key => { data.delete(key) },
    setItem: (key, value) => { data.set(key, String(value)) },
  }
}

describe('local mobile settings', () => {
  it('defaults: not onboarded, assistant off, no server', () => {
    expect(loadSettings(memoryStorage())).toEqual({ onboarded: false, assistantOn: false, server: { url: '', token: '' } })
  })

  it('round-trips and tolerates corrupted values', () => {
    const storage = memoryStorage()
    saveSettings(storage, { onboarded: true, assistantOn: true, server: { url: 'https://n8n.example.com', token: 't' } })
    expect(loadSettings(storage)).toEqual({ onboarded: true, assistantOn: true, server: { url: 'https://n8n.example.com', token: 't' } })
    storage.setItem(SETTINGS_KEYS.server, '{bad')
    expect(loadSettings(storage).server).toEqual({ url: '', token: '' })
  })

  it('survives a storage that throws', () => {
    const broken = { getItem: () => { throw new Error('denied') }, setItem: () => { throw new Error('denied') } } as unknown as Storage
    expect(loadSettings(broken).onboarded).toBe(false)
    expect(() => saveSettings(broken, { onboarded: true, assistantOn: false, server: { url: '', token: '' } })).not.toThrow()
  })
})
