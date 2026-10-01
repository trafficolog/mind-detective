// n8n transport (ADR 017): one base URL, two webhooks. Model/STT keys live in n8n Credentials.
export type FetchLike = (input: string, init?: RequestInit) => Promise<Response>

const defaultFetch: FetchLike = (input, init) => fetch(input, init)

export interface ServerConfigInput {
  url?: string
  token?: string
}

export interface SttConfigInput {
  url?: string
  model?: string
  key?: string
}

export const STT_DEFAULT_MODEL = 'whisper-1'

function allowedUrl(value: string): URL | null {
  try {
    const url = new URL(value)
    return url.protocol === 'https:' || url.hostname === 'localhost' || url.hostname === '127.0.0.1' ? url : null
  } catch {
    return null
  }
}

export function serverEndpoints(cfg: ServerConfigInput): { propose: string, transcribe: string, token: string } {
  const base = String(cfg?.url ?? '').trim().replace(/\/+$/, '')
  if (!allowedUrl(base)) throw new Error('server_config_invalid')
  return {
    propose: `${base}/webhook/md-propose`,
    transcribe: `${base}/webhook/md-transcribe`,
    token: String(cfg.token ?? '').trim(),
  }
}

export function serverReady(cfg: ServerConfigInput): boolean {
  try {
    serverEndpoints(cfg)
    return true
  } catch {
    return false
  }
}

export function serverStt(cfg: ServerConfigInput): { url: string, key: string } {
  const endpoints = serverEndpoints(cfg)
  return { url: endpoints.transcribe, key: endpoints.token }
}

export function serverComplete(cfg: ServerConfigInput, fetchImpl: FetchLike = defaultFetch): (prompt: string) => Promise<string> {
  return async (prompt: string) => {
    const endpoints = serverEndpoints(cfg)
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (endpoints.token) headers.Authorization = `Bearer ${endpoints.token}`
    const response = await fetchImpl(endpoints.propose, { method: 'POST', headers, body: JSON.stringify({ prompt }) })
    if (!response.ok) throw new Error('server_unavailable')
    const body = await response.json() as { text?: unknown }
    return String(body?.text ?? '')
  }
}

export function validateSttConfig(cfg: SttConfigInput): { url: string, model: string, key: string } {
  const url = String(cfg?.url ?? '').trim()
  if (!allowedUrl(url)) throw new Error('stt_config_invalid')
  return { url, model: String(cfg.model ?? '').trim() || STT_DEFAULT_MODEL, key: String(cfg.key ?? '').trim() }
}

export function sttReady(cfg: SttConfigInput): boolean {
  try {
    validateSttConfig(cfg)
    return true
  } catch {
    return false
  }
}

export async function transcribe(cfg: SttConfigInput, audio: Blob, fetchImpl: FetchLike = defaultFetch, language = 'ru'): Promise<string> {
  const config = validateSttConfig(cfg)
  if (!audio || audio.size === 0) throw new Error('stt_empty')
  const form = new FormData()
  form.append('file', audio, `speech.${String(audio.type).includes('mp4') ? 'mp4' : 'webm'}`)
  form.append('model', config.model)
  form.append('language', language)
  form.append('response_format', 'json')
  let response: Response
  try {
    response = await fetchImpl(config.url, {
      method: 'POST',
      headers: config.key ? { Authorization: `Bearer ${config.key}` } : {},
      body: form,
    })
  } catch {
    throw new Error('stt_unavailable')
  }
  if (!response.ok) throw new Error('stt_unavailable')
  let body: { text?: unknown }
  try {
    body = await response.json() as { text?: unknown }
  } catch {
    throw new Error('stt_unavailable')
  }
  const text = String(body?.text ?? '').trim()
  if (!text) throw new Error('stt_empty')
  return text
}
