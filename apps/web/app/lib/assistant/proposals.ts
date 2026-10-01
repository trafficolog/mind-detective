// Research-only assistant boundary (ADR 017). Nothing here mutates a Case:
// proposals become data only after an explicit user action through the command path.
import type { CaseV2 } from '../api/contracts'
import { itemKind, nextZone, timelineView, zonesView } from '../mobile/viewModel'
import { vocab } from '../mobile/vocab'

export type ProposalKind = 'question' | 'check'
export type ProposalSource = 'assistant' | 'fallback' | 'checklist'

export interface Proposal {
  kind: ProposalKind
  text: string
  place?: string
}

export interface SourcedProposal extends Proposal {
  source: ProposalSource
  reason?: 'rejected' | 'unavailable'
}

export class ProposalRejected extends Error {
  constructor() {
    super('proposal_rejected')
    this.name = 'ProposalRejected'
  }
}

export interface AssistantContext {
  item: string
  kind: 'physical' | 'digital'
  mode: string
  confirmed: string[]
  events: Array<{ title: string, time: string | null, precision: string }>
  contradictions: string[]
  zones: Array<{ name: string, state: string }>
}

/** I1/I8: minimal context — no free account, no hypotheses, no search suggestions as memories. */
export function assistantContext(caseValue: CaseV2): AssistantContext {
  return {
    item: caseValue.item_label,
    kind: itemKind(caseValue),
    mode: caseValue.current_mode,
    confirmed: caseValue.statements
      .filter(statement => statement.statement_type !== 'hypothesis' && statement.statement_type !== 'search_suggestion')
      .map(statement => statement.original_text),
    events: (caseValue.timeline?.events ?? []).map(event => ({
      title: event.label,
      time: event.event_time,
      precision: event.time_precision,
    })),
    contradictions: timelineView(caseValue).contradictions,
    zones: zonesView(caseValue).map(zone => ({ name: zone.name, state: zone.label })),
  }
}

export function assistantPrompt(caseValue: CaseV2): string {
  const search = caseValue.current_mode === 'search'
  const digital = itemKind(caseValue) === 'digital'
  const task = search
    ? digital
      ? 'Режим: поиск цифрового файла. Предложи ОДИН конкретный источник (устройство, приложение, папка, альбом), которого нет среди проверенных. Не проси доступ к файлам — проверяет пользователь сам.'
      : 'Режим: поиск. Предложи ОДНУ конкретную физическую проверку места, которого нет среди проверенных.'
    : 'Режим: реконструкция. Задай ОДИН уточняющий вопрос о последовательности событий.'
  const shape = search
    ? '{"kind":"check","text":"до 160 символов по-русски","place":"короткое название места"}'
    : '{"kind":"question","text":"до 160 символов по-русски"}'
  return 'Ты помощник систематического поиска потерянной вещи. Не угадывай, где вещь. Не называй вероятности. Не утверждай факты за пользователя.\n'
    + task
    + `\nВерни только JSON: ${shape}\nКонтекст: ${JSON.stringify(assistantContext(caseValue))}`
}

const FORBIDDEN = /\d+\s*%|вероятн|скорее всего|наверн|уверен|точно (там|в )|мы (знаем|найд)|найд[её]м|местонахожд/i

function need(condition: unknown): void {
  if (!condition) throw new ProposalRejected()
}

export function guardProposal(raw: string, caseValue: CaseV2): Proposal {
  let parsed: Record<string, unknown>
  try {
    const match = /\{[\s\S]*\}/.exec(String(raw))
    parsed = JSON.parse(match![0]) as Record<string, unknown>
  } catch {
    throw new ProposalRejected()
  }
  need(parsed && typeof parsed === 'object')
  const text = String(parsed.text ?? '').trim()
  const place = String(parsed.place ?? '').trim()
  need(parsed.kind === 'question' || parsed.kind === 'check')
  need(text.length >= 5 && text.length <= 200 && !FORBIDDEN.test(text))
  if (parsed.kind === 'question') return { kind: 'question', text }
  need(caseValue.current_mode === 'search' && place.length >= 2 && place.length <= 60 && !FORBIDDEN.test(place))
  const key = place.toLowerCase()
  need(!zonesView(caseValue).some(zone => zone.name.toLowerCase() === key && zone.done))
  return { kind: 'check', text, place }
}

export function fallbackProposal(caseValue: CaseV2): Proposal {
  const words = vocab(itemKind(caseValue))
  if (caseValue.current_mode === 'search') {
    const zone = nextZone(caseValue)
    return zone ? { kind: 'check', place: zone.name, text: `Проверьте: ${zone.name}` } : { kind: 'question', text: words.noPlace }
  }
  const unknown = timelineView(caseValue).firstUnknownTitle
  return { kind: 'question', text: unknown ? `Что вы помните о событии «${unknown}»?` : words.lastSeen }
}

export type CompleteFn = (prompt: string) => Promise<string>

export async function proposalFlow(caseValue: CaseV2, complete: CompleteFn, timeoutMs = 10_000): Promise<SourcedProposal> {
  let timer: ReturnType<typeof setTimeout> | undefined
  try {
    const raw = await Promise.race([
      complete(assistantPrompt(caseValue)),
      new Promise<never>((_, reject) => { timer = setTimeout(() => reject(new Error('timeout')), timeoutMs) }),
    ])
    return { ...guardProposal(raw, caseValue), source: 'assistant' }
  } catch (error) {
    return {
      ...fallbackProposal(caseValue),
      source: 'fallback',
      reason: error instanceof ProposalRejected ? 'rejected' : 'unavailable',
    }
  } finally {
    if (timer) clearTimeout(timer)
  }
}

export function checklistProposal(caseValue: CaseV2): SourcedProposal {
  return { ...fallbackProposal(caseValue), source: 'checklist' }
}
