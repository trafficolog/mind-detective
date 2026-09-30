import { serverReady, serverStt, transcribe } from '~/lib/assistant/server'
import { errorMessage } from '~/lib/mobile/commands'

type Recognizer = { lang: string, interimResults: boolean, continuous: boolean, onresult: ((event: any) => void) | null, onerror: ((event: any) => void) | null, onend: (() => void) | null, start(): void, stop(): void }
type Active = { stop(discard?: boolean): void }

// One microphone session per page, shared by every field.
let active: Active | null = null

/**
 * Voice input: n8n configured → MediaRecorder → md-transcribe; otherwise Web Speech API (ru-RU).
 * Text is appended to the field only; saving always needs an explicit button press.
 */
export function useDictation() {
  const { settings } = useMobileSettings()
  const listening = useState<string | null>('md-dictation-listening', () => null)
  const transcribing = useState<string | null>('md-dictation-transcribing', () => null)
  const dictationError = useState<string | null>('md-dictation-error', () => null)

  const useServer = computed(() => serverReady(settings.value.server))
  const available = computed(() => {
    if (typeof window === 'undefined') return false
    const w = window as unknown as Record<string, unknown>
    return useServer.value
      ? Boolean(w.MediaRecorder && navigator.mediaDevices)
      : Boolean(w.SpeechRecognition || w.webkitSpeechRecognition)
  })

  function joinText(base: string, addition: string): string {
    return base + (base && !/\s$/.test(base) ? ' ' : '') + addition
  }

  function stop(discard = true): void {
    active?.stop(discard)
    active = null
  }

  async function recordWithServer(field: string, base: string, apply: (text: string) => void): Promise<void> {
    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      dictationError.value = 'Нет доступа к микрофону.'
      return
    }
    const chunks: Blob[] = []
    const recorder = new MediaRecorder(stream)
    let discarded = false
    recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data) }
    recorder.onstop = async () => {
      stream.getTracks().forEach(track => track.stop())
      listening.value = null
      if (discarded) return
      transcribing.value = field
      try {
        apply(joinText(base, await transcribe(serverStt(settings.value.server), new Blob(chunks, { type: recorder.mimeType }))))
      } catch (error) {
        dictationError.value = errorMessage(error instanceof Error ? error.message : '', 'physical')
      } finally {
        transcribing.value = null
      }
    }
    active = { stop: (discard?: boolean) => { discarded = Boolean(discard); recorder.stop() } }
    listening.value = field
    recorder.start()
  }

  function recordWithBrowser(field: string, base: string, apply: (text: string) => void): void {
    const w = window as unknown as Record<string, new () => Recognizer>
    const SR = w.SpeechRecognition || w.webkitSpeechRecognition
    if (!SR) {
      dictationError.value = 'Голосовой ввод не поддерживается в этом браузере.'
      return
    }
    const recognizer = new SR()
    recognizer.lang = 'ru-RU'
    recognizer.interimResults = true
    recognizer.continuous = true
    let finalText = ''
    recognizer.onresult = (event) => {
      let interim = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript as string
        if (event.results[i].isFinal) finalText += transcript
        else interim += transcript
      }
      apply(joinText(base, finalText + interim))
    }
    recognizer.onerror = (event) => {
      active = null
      listening.value = null
      dictationError.value = event?.error === 'not-allowed' ? 'Нет доступа к микрофону.' : 'Не удалось распознать речь.'
    }
    recognizer.onend = () => { active = null; listening.value = null }
    active = { stop: () => recognizer.stop() }
    listening.value = field
    try {
      recognizer.start()
    } catch {
      active = null
      listening.value = null
    }
  }

  /** Toggles dictation for a field; `current` is the field text at start, `apply` receives the whole new text. */
  async function toggle(field: string, current: string, apply: (text: string) => void): Promise<void> {
    if (transcribing.value) return
    if (active) {
      active.stop(false)
      active = null
      return
    }
    dictationError.value = null
    if (useServer.value) {
      if (typeof MediaRecorder === 'undefined' || !navigator.mediaDevices) {
        dictationError.value = 'Запись звука не поддерживается в этом браузере.'
        return
      }
      await recordWithServer(field, current, apply)
      return
    }
    recordWithBrowser(field, current, apply)
  }

  function label(field: string): string {
    return listening.value === field ? 'Остановить' : transcribing.value === field ? 'Распознаю…' : 'Надиктовать'
  }

  function icon(field: string): string {
    return listening.value === field ? 'mic-off' : 'mic'
  }

  return { available, listening, transcribing, dictationError, toggle, stop, label, icon }
}
