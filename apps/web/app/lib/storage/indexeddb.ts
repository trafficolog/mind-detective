import type { CaseV2 } from '../api/contracts'

const DB_NAME = 'mind-detective'
const DB_VERSION = 1
const CASE_STORE = 'cases'

export interface CaseRepository {
  list(): Promise<CaseV2[]>
  get(caseId: string): Promise<CaseV2 | null>
  put(caseValue: CaseV2): Promise<void>
  delete(caseId: string): Promise<void>
}

function requestResult<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error ?? new Error('MD_WEB_IDB_REQUEST'))
  })
}

function transactionDone(transaction: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve()
    transaction.onerror = () => reject(transaction.error ?? new Error('MD_WEB_IDB_TRANSACTION'))
    transaction.onabort = () => reject(transaction.error ?? new Error('MD_WEB_IDB_ABORT'))
  })
}

export function openCaseDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === 'undefined') {
    return Promise.reject(new Error('MD_WEB_IDB_UNAVAILABLE'))
  }
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    request.onupgradeneeded = () => {
      const database = request.result
      if (!database.objectStoreNames.contains(CASE_STORE)) {
        database.createObjectStore(CASE_STORE, { keyPath: 'case_id' })
      }
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error ?? new Error('MD_WEB_IDB_OPEN'))
  })
}

export function createIndexedDbCaseRepository(): CaseRepository {
  return {
    async list() {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(CASE_STORE, 'readonly')
        const values = await requestResult(transaction.objectStore(CASE_STORE).getAll())
        await transactionDone(transaction)
        return (values as CaseV2[]).sort((a, b) => b.updated_at.localeCompare(a.updated_at))
      } finally {
        database.close()
      }
    },
    async get(caseId) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(CASE_STORE, 'readonly')
        const value = await requestResult(transaction.objectStore(CASE_STORE).get(caseId))
        await transactionDone(transaction)
        return (value as CaseV2 | undefined) ?? null
      } finally {
        database.close()
      }
    },
    async put(caseValue) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(CASE_STORE, 'readwrite')
        transaction.objectStore(CASE_STORE).put(structuredClone(caseValue))
        await transactionDone(transaction)
      } finally {
        database.close()
      }
    },
    async delete(caseId) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(CASE_STORE, 'readwrite')
        transaction.objectStore(CASE_STORE).delete(caseId)
        await transactionDone(transaction)
      } finally {
        database.close()
      }
    },
  }
}

export async function requestPersistentStorage(): Promise<'granted' | 'denied' | 'unsupported'> {
  if (typeof navigator === 'undefined' || !navigator.storage?.persisted || !navigator.storage?.persist) {
    return 'unsupported'
  }
  if (await navigator.storage.persisted()) {
    return 'granted'
  }
  return (await navigator.storage.persist()) ? 'granted' : 'denied'
}
