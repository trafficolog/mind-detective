import { describe, expect, it } from 'vitest'
import { proposalFlow } from '../../app/lib/assistant/proposals'
import { serverComplete, serverEndpoints, serverReady, serverStt, sttReady, transcribe, validateSttConfig } from '../../app/lib/assistant/server'
import { CaseBuilder } from './support/mobileCases'

const fakeRes = (ok: boolean, body: unknown) => ({ ok, json: async () => body }) as unknown as Response
const blob = () => new Blob(['x'], { type: 'audio/webm' })

async function rejectsWith(fn: () => Promise<unknown>, code: string): Promise<void> {
  await expect(fn()).rejects.toThrow(code)
}

describe('n8n server and speech-to-text transport', () => {
  it('T32 STT config accepts https or localhost only', () => {
    expect(validateSttConfig({ url: 'https://a.b/v1/audio/transcriptions' }).model).toBe('whisper-1')
    expect(sttReady({ url: 'http://localhost:8000/x' })).toBe(true)
    expect(sttReady({ url: 'http://127.0.0.1:5678/x' })).toBe(true)
    expect(sttReady({ url: 'http://evil.com/x' })).toBe(false)
    expect(sttReady({ url: '' })).toBe(false)
  })

  it('T33 transcribe sends multipart with model, language and bearer key', async () => {
    let seen: RequestInit | undefined
    const text = await transcribe({ url: 'https://a.b/t', key: 'k' }, blob(), async (_url, init) => { seen = init; return fakeRes(true, { text: ' привет  ' }) })
    expect(text).toBe('привет')
    expect((seen?.headers as Record<string, string>).Authorization).toBe('Bearer k')
    const body = seen?.body as FormData
    expect([body.get('model'), body.get('language'), body.get('response_format')]).toEqual(['whisper-1', 'ru', 'json'])
    expect((body.get('file') as File).name).toBe('speech.webm')
  })

  it('T34 network or HTTP error → stt_unavailable', async () => {
    await rejectsWith(() => transcribe({ url: 'https://a.b/t' }, blob(), async () => { throw new Error('x') }), 'stt_unavailable')
    await rejectsWith(() => transcribe({ url: 'https://a.b/t' }, blob(), async () => fakeRes(false, {})), 'stt_unavailable')
  })

  it('T35 empty answer or empty recording → stt_empty', async () => {
    await rejectsWith(() => transcribe({ url: 'https://a.b/t' }, blob(), async () => fakeRes(true, { text: ' ' })), 'stt_empty')
    await rejectsWith(() => transcribe({ url: 'https://a.b/t' }, new Blob([]), async () => fakeRes(true, { text: 'a' })), 'stt_empty')
  })

  it('T45 endpoints derive from the base address, https/localhost only', () => {
    const e = serverEndpoints({ url: 'https://n8n.example.com/', token: 't' })
    expect([e.propose, e.transcribe, e.token]).toEqual([
      'https://n8n.example.com/webhook/md-propose', 'https://n8n.example.com/webhook/md-transcribe', 't',
    ])
    expect(serverReady({ url: 'http://x.com', token: '' })).toBe(false)
    expect(serverReady({ url: 'http://localhost:5678', token: '' })).toBe(true)
    expect(serverStt({ url: 'https://n8n.example.com', token: 't' })).toEqual({ url: 'https://n8n.example.com/webhook/md-transcribe', key: 't' })
  })

  it('T46 propose sends only the prompt and returns model text', async () => {
    let seen: { url: string, init: RequestInit } | undefined
    const complete = serverComplete({ url: 'https://n8n.example.com', token: 't' }, async (url, init) => {
      seen = { url: String(url), init: init! }
      return fakeRes(true, { text: '{"kind":"question","text":"Что было дальше?"}' })
    })
    const raw = await complete('P')
    expect(seen?.url).toBe('https://n8n.example.com/webhook/md-propose')
    expect(JSON.parse(String(seen?.init.body))).toEqual({ prompt: 'P' })
    expect((seen?.init.headers as Record<string, string>).Authorization).toBe('Bearer t')
    expect(JSON.parse(raw).kind).toBe('question')
  })

  it('T47 unavailable n8n falls back to the checklist', async () => {
    const c = CaseBuilder.create().search().target('A').value
    const p = await proposalFlow(c, serverComplete({ url: 'https://n8n.example.com', token: '' }, async () => fakeRes(false, {})))
    expect(p).toMatchObject({ source: 'fallback', reason: 'unavailable', place: 'A' })
  })
})
