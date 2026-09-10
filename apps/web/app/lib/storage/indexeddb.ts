import type { CaseV2 } from '../api/contracts'

const DB_NAME = 'mind-detective'
export const DB_VERSION = 2
const CASE_STORE = 'cases'
export const EXECUTION_RECEIPT_STORE = 'execution_receipts'
const RECEIPT_CASE_INDEX = 'case_id'

export interface ExecutionReceipt {
  command_id: string
  case_id: string
  contract_version: string
  input_case_hash: string
  output_case_hash: string
  applied_at: string
}

export interface ReceiptInputIdentity {
  command_id: string
  case_id: string
  contract_version: string
  input_case_hash: string
}

export interface CaseRepository {
  list(): Promise<CaseV2[]>
  get(caseId: string): Promise<CaseV2 | null>
  put(caseValue: CaseV2): Promise<void>
  createOnly(caseValue: CaseV2): Promise<CaseV2>
  getReceipt(commandId: string): Promise<ExecutionReceipt | null>
  applyWithReceipt(caseValue: CaseV2, receipt: ExecutionReceipt): Promise<CaseV2>
  delete(caseId: string): Promise<void>
}

export function createIdentityMatches(left: CaseV2, right: CaseV2): boolean {
  return left.case_id === right.case_id
    && left.item_label === right.item_label
    && left.created_at === right.created_at
}

export function receiptInputMatches(receipt: ExecutionReceipt, identity: ReceiptInputIdentity): boolean {
  return receipt.command_id === identity.command_id
    && receipt.case_id === identity.case_id
    && receipt.contract_version === identity.contract_version
    && receipt.input_case_hash === identity.input_case_hash
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
      if (!database.objectStoreNames.contains(EXECUTION_RECEIPT_STORE)) {
        const receipts = database.createObjectStore(EXECUTION_RECEIPT_STORE, { keyPath: 'command_id' })
        receipts.createIndex(RECEIPT_CASE_INDEX, 'case_id', { unique: false })
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
        const done = transactionDone(transaction)
        const values = await requestResult(transaction.objectStore(CASE_STORE).getAll())
        await done
        return (values as CaseV2[]).sort((a, b) => b.updated_at.localeCompare(a.updated_at))
      } finally {
        database.close()
      }
    },
    async get(caseId) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(CASE_STORE, 'readonly')
        const done = transactionDone(transaction)
        const value = await requestResult(transaction.objectStore(CASE_STORE).get(caseId))
        await done
        return (value as CaseV2 | undefined) ?? null
      } finally {
        database.close()
      }
    },
    async put(caseValue) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(CASE_STORE, 'readwrite')
        const done = transactionDone(transaction)
        transaction.objectStore(CASE_STORE).put(structuredClone(caseValue))
        await done
      } finally {
        database.close()
      }
    },
    async createOnly(caseValue) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(CASE_STORE, 'readwrite')
        const done = transactionDone(transaction)
        const store = transaction.objectStore(CASE_STORE)
        const existing = await requestResult(store.get(caseValue.case_id)) as CaseV2 | undefined
        if (existing !== undefined) {
          if (!createIdentityMatches(existing, caseValue)) {
            transaction.abort()
            try { await done } catch { /* expected abort */ }
            throw new Error('MD_WEB_CASE_ID_CONFLICT')
          }
          await done
          return existing
        }
        store.add(structuredClone(caseValue))
        await done
        return caseValue
      } finally {
        database.close()
      }
    },
    async getReceipt(commandId) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction(EXECUTION_RECEIPT_STORE, 'readonly')
        const done = transactionDone(transaction)
        const value = await requestResult(transaction.objectStore(EXECUTION_RECEIPT_STORE).get(commandId))
        await done
        return (value as ExecutionReceipt | undefined) ?? null
      } finally {
        database.close()
      }
    },
    async applyWithReceipt(caseValue, receipt) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction([CASE_STORE, EXECUTION_RECEIPT_STORE], 'readwrite')
        const done = transactionDone(transaction)
        const caseStore = transaction.objectStore(CASE_STORE)
        const receiptStore = transaction.objectStore(EXECUTION_RECEIPT_STORE)
        const existingReceipt = await requestResult(receiptStore.get(receipt.command_id)) as ExecutionReceipt | undefined
        if (existingReceipt !== undefined) {
          if (!receiptInputMatches(existingReceipt, receipt)) {
            transaction.abort()
            try { await done } catch { /* expected abort */ }
            throw new Error('MD_WEB_COMMAND_ID_CONFLICT')
          }
          const currentCase = await requestResult(caseStore.get(receipt.case_id)) as CaseV2 | undefined
          await done
          if (currentCase === undefined) throw new Error('MD_WEB_CASE_NOT_FOUND')
          return currentCase
        }
        caseStore.put(structuredClone(caseValue))
        receiptStore.add(structuredClone(receipt))
        await done
        return caseValue
      } finally {
        database.close()
      }
    },
    async delete(caseId) {
      const database = await openCaseDatabase()
      try {
        const transaction = database.transaction([CASE_STORE, EXECUTION_RECEIPT_STORE], 'readwrite')
        const done = transactionDone(transaction)
        transaction.objectStore(CASE_STORE).delete(caseId)
        const receiptStore = transaction.objectStore(EXECUTION_RECEIPT_STORE)
        const receiptKeys = await requestResult(
          receiptStore.index(RECEIPT_CASE_INDEX).getAllKeys(IDBKeyRange.only(caseId)),
        )
        for (const key of receiptKeys) receiptStore.delete(key)
        await done
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
