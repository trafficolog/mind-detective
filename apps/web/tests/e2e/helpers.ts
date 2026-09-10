import type { Page } from '@playwright/test'
import type { CaseV2, CandidateCheckV2, JournalEntryV2, SearchCheckV2 } from '../../app/lib/api/contracts'

export function candidate(
  id: string,
  target: string,
  checkState: CandidateCheckV2['check_state'] = 'unchecked',
): CandidateCheckV2 {
  return {
    id,
    target,
    route_relation: 'direct',
    check_state: checkState,
    effort: 'low',
    safety: 'safe',
    urgency_relevance: 'normal',
    basis: 'episode',
    based_on: [],
    rationale: ['episode-linked'],
  }
}

export function searchCheck(
  id: string,
  candidateId: string,
  target: string,
  method: SearchCheckV2['method'] = 'reported_check',
): SearchCheckV2 {
  return {
    id,
    target,
    method,
    started_at: '2026-09-10T07:01:00Z',
    completed_at: '2026-09-10T07:01:10Z',
    result: 'not_found',
    inaccessible_parts: [],
    based_on: [candidateId],
    notes: [],
  }
}

export function journalEntry(
  id: string,
  mode: JournalEntryV2['mode'],
  text: string,
): JournalEntryV2 {
  return {
    id,
    author: mode === 'system' ? 'system' : 'user',
    mode,
    entry_type: mode === 'system' ? 'system_event' : 'statement',
    text,
    created_at: '2026-09-10T07:01:00Z',
    statement_ids: [],
    search_check_ids: [],
  }
}

export function caseFixture(overrides: Partial<CaseV2> = {}): CaseV2 {
  return {
    schema: 'mind-detective-case/v2',
    case_id: 'case-e2e',
    item_label: 'ключи',
    created_at: '2026-09-10T07:00:00Z',
    updated_at: '2026-09-10T07:00:00Z',
    lifecycle: 'active',
    statements: [],
    timeline: null,
    search_checks: [],
    candidates: [candidate('candidate-1', 'карманы куртки')],
    next_action: null,
    constraints: [],
    outcome: null,
    current_mode: 'search',
    interaction_journal: [],
    action_feedback: [],
    ...overrides,
  }
}

export async function seedCase(page: Page, caseValue: CaseV2): Promise<void> {
  await page.goto('/')
  await page.evaluate(async (payload) => {
    await new Promise<void>((resolve, reject) => {
      const request = indexedDB.open('mind-detective')
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction('cases', 'readwrite')
        transaction.objectStore('cases').put(payload)
        transaction.oncomplete = () => {
          database.close()
          resolve()
        }
        transaction.onerror = () => reject(transaction.error)
      }
    })
  }, caseValue)
}

export async function storedCase(page: Page, caseId: string): Promise<CaseV2 | null> {
  return await page.evaluate(async (id) => {
    return await new Promise<CaseV2 | null>((resolve, reject) => {
      const request = indexedDB.open('mind-detective')
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction('cases', 'readonly')
        const get = transaction.objectStore('cases').get(id)
        get.onsuccess = () => {
          const result = (get.result as CaseV2 | undefined) ?? null
          database.close()
          resolve(result)
        }
        get.onerror = () => reject(get.error)
      }
    })
  }, caseId)
}
