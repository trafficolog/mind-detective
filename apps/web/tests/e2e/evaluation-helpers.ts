import type { Page } from '@playwright/test'
import type { EvaluationEventV1, EvaluationSessionV1 } from '../../app/lib/eval/contracts'
import { EVALUATION_DB_VERSION } from '../../app/lib/eval/store'

async function ensureEvaluationDatabase(page: Page): Promise<void> {
  await page.evaluate(async (version) => {
    await new Promise<void>((resolve, reject) => {
      const request = indexedDB.open('mind-detective-evaluation', version)
      request.onupgradeneeded = () => {
        const database = request.result
        if (!database.objectStoreNames.contains('participants')) {
          database.createObjectStore('participants', { keyPath: 'participant_id' })
        }
        if (!database.objectStoreNames.contains('sessions')) {
          const sessions = database.createObjectStore('sessions', { keyPath: 'evaluation_session_id' })
          sessions.createIndex('case_id', 'case_id', { unique: true })
        }
        if (!database.objectStoreNames.contains('events')) {
          const events = database.createObjectStore('events', { keyPath: 'event_id' })
          events.createIndex('evaluation_session_id', 'evaluation_session_id', { unique: false })
        }
      }
      request.onerror = () => reject(request.error)
      request.onblocked = () => reject(new Error('MD_WEB_EVAL_TEST_IDB_BLOCKED'))
      request.onsuccess = () => {
        request.result.close()
        resolve()
      }
    })
  }, EVALUATION_DB_VERSION)
}

export async function storedEvaluationSessions(page: Page): Promise<EvaluationSessionV1[]> {
  await ensureEvaluationDatabase(page)
  return await page.evaluate(async (version) => {
    return await new Promise<EvaluationSessionV1[]>((resolve, reject) => {
      const request = indexedDB.open('mind-detective-evaluation', version)
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction('sessions', 'readonly')
        const get = transaction.objectStore('sessions').getAll()
        get.onsuccess = () => {
          database.close()
          resolve(get.result as EvaluationSessionV1[])
        }
        get.onerror = () => {
          database.close()
          reject(get.error)
        }
      }
    })
  }, EVALUATION_DB_VERSION)
}

export async function storedEvaluationEvents(page: Page): Promise<EvaluationEventV1[]> {
  await ensureEvaluationDatabase(page)
  return await page.evaluate(async (version) => {
    return await new Promise<EvaluationEventV1[]>((resolve, reject) => {
      const request = indexedDB.open('mind-detective-evaluation', version)
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction('events', 'readonly')
        const get = transaction.objectStore('events').getAll()
        get.onsuccess = () => {
          database.close()
          resolve(get.result as EvaluationEventV1[])
        }
        get.onerror = () => {
          database.close()
          reject(get.error)
        }
      }
    })
  }, EVALUATION_DB_VERSION)
}
