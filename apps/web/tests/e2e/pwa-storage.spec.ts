import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { expect, test } from '@playwright/test'
import { DB_VERSION, type ExecutionReceipt } from '../../app/lib/storage/indexeddb'
import { caseFixture, seedCase, storedCase } from './helpers'

test('generated PWA precaches shell assets without API case or background-sync data', async () => {
  const output = resolve(process.cwd(), '.output/public')
  const worker = readFileSync(resolve(output, 'sw.js'), 'utf8')
  const manifest = JSON.parse(readFileSync(resolve(process.cwd(), 'public/manifest.webmanifest'), 'utf8')) as {
    display?: string
    start_url?: string
  }

  expect(manifest.display).toBe('standalone')
  expect(manifest.start_url).toBe('/')
  expect(worker).toContain('index.html')
  expect(worker).not.toMatch(/BackgroundSyncPlugin|workbox-background-sync|backgroundSync/)
  expect(worker).not.toMatch(/"url":"\/api\//)
  expect(worker).not.toMatch(/mind-detective-case\/v2|item_label|interaction_journal|evaluation-export/)
  expect(worker).not.toMatch(/"url":"\/?(?:200|404)(?:\.html)?"/)
})

test('failed IndexedDB commit leaves canonical case unchanged and retry reuses the same local envelope', async ({ page }) => {
  const caseValue = caseFixture()
  let commandApiCalls = 0
  page.on('request', (request) => {
    try {
      if (new URL(request.url()).pathname === '/api/v1/case/command') commandApiCalls += 1
    } catch {
      // Ignore browser internals.
    }
  })

  await seedCase(page, caseValue)
  await page.goto(`/cases/${caseValue.case_id}`)

  await page.evaluate(async ({ version, caseId }) => {
    await new Promise<void>((resolvePromise, reject) => {
      const request = indexedDB.open('mind-detective', version)
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction('execution_receipts', 'readwrite')
        transaction.objectStore('execution_receipts').add({
          command_id: 'forced-conflict',
          case_id: caseId,
          contract_version: 'mind-detective-local-execution/v1',
          input_case_hash: 'sha256:fixture-input',
          output_case_hash: 'sha256:fixture-output',
          applied_at: '2026-09-10T07:00:30Z',
        })
        transaction.oncomplete = () => {
          database.close()
          resolvePromise()
        }
        transaction.onerror = () => {
          database.close()
          reject(transaction.error)
        }
      }
    })
  }, { version: DB_VERSION, caseId: caseValue.case_id })

  await page.evaluate(() => {
    const prototype = IDBObjectStore.prototype
    const nativeAdd = prototype.add
    ;(window as typeof window & { __mdNativeAdd?: typeof nativeAdd; __mdIntendedReceipt?: unknown }).__mdNativeAdd = nativeAdd
    prototype.add = function (value: unknown, key?: IDBValidKey): IDBRequest<IDBValidKey> {
      if (this.name === 'execution_receipts'
        && value !== null
        && typeof value === 'object'
        && 'command_id' in value
        && (value as { command_id?: unknown }).command_id !== 'forced-conflict') {
        const intended = structuredClone(value)
        ;(window as typeof window & { __mdIntendedReceipt?: unknown }).__mdIntendedReceipt = intended
        const conflicting = { ...(value as Record<string, unknown>), command_id: 'forced-conflict' }
        return key === undefined ? nativeAdd.call(this, conflicting) : nativeAdd.call(this, conflicting, key)
      }
      return key === undefined ? nativeAdd.call(this, value) : nativeAdd.call(this, value, key)
    }
  })

  await page.getByTestId('mark-checked').click()

  await expect(page.getByTestId('command-error')).toBeVisible()
  await expect(page.getByTestId('progress-checked')).toContainText('0')
  expect((await storedCase(page, caseValue.case_id))?.search_checks).toHaveLength(0)

  const intended = await page.evaluate(() => {
    return (window as typeof window & { __mdIntendedReceipt?: ExecutionReceipt }).__mdIntendedReceipt ?? null
  })
  expect(intended).not.toBeNull()
  expect(intended?.command_id).toBeTruthy()

  await page.evaluate(() => {
    const state = window as typeof window & { __mdNativeAdd?: typeof IDBObjectStore.prototype.add }
    if (!state.__mdNativeAdd) throw new Error('MD_WEB_TEST_IDB_ADD_NOT_PATCHED')
    IDBObjectStore.prototype.add = state.__mdNativeAdd
    delete state.__mdNativeAdd
  })

  await page.getByTestId('retry-command').click()
  await expect(page.getByTestId('progress-checked')).toContainText('1')
  expect((await storedCase(page, caseValue.case_id))?.search_checks).toHaveLength(1)

  const persistedReceipt = await page.evaluate(async ({ version, commandId }) => {
    return await new Promise<ExecutionReceipt | null>((resolvePromise, reject) => {
      const request = indexedDB.open('mind-detective', version)
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction('execution_receipts', 'readonly')
        const get = transaction.objectStore('execution_receipts').get(commandId)
        get.onsuccess = () => {
          const result = (get.result as ExecutionReceipt | undefined) ?? null
          database.close()
          resolvePromise(result)
        }
        get.onerror = () => {
          database.close()
          reject(get.error)
        }
      }
    })
  }, { version: DB_VERSION, commandId: intended!.command_id })

  expect(persistedReceipt).toEqual(intended)
  expect(Object.keys(persistedReceipt ?? {}).sort()).toEqual([
    'applied_at',
    'case_id',
    'command_id',
    'contract_version',
    'input_case_hash',
    'output_case_hash',
  ])
  expect(commandApiCalls).toBe(0)
})
