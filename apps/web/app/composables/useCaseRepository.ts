import { readonly, type DeepReadonly, type Ref } from 'vue'
import type { CaseV2 } from '~/lib/api/contracts'
import {
  createIndexedDbCaseRepository,
  type ExecutionReceipt,
} from '~/lib/storage/indexeddb'

const repository = createIndexedDbCaseRepository()

export interface CaseRepositoryComposable {
  cases: DeepReadonly<Ref<CaseV2[]>>
  refresh(): Promise<CaseV2[]>
  get(caseId: string): Promise<CaseV2 | null>
  put(caseValue: CaseV2): Promise<void>
  createOnly(caseValue: CaseV2): Promise<CaseV2>
  getReceipt(commandId: string): Promise<ExecutionReceipt | null>
  applyWithReceipt(caseValue: CaseV2, receipt: ExecutionReceipt): Promise<CaseV2>
  remove(caseId: string): Promise<void>
}

export function useCaseRepository(): CaseRepositoryComposable {
  const cases = useState<CaseV2[]>('mind-detective-cases', () => [])

  async function refresh(): Promise<CaseV2[]> {
    cases.value = await repository.list()
    return cases.value
  }

  async function get(caseId: string): Promise<CaseV2 | null> {
    return await repository.get(caseId)
  }

  async function put(caseValue: CaseV2): Promise<void> {
    await repository.put(caseValue)
    await refresh()
  }

  async function createOnly(caseValue: CaseV2): Promise<CaseV2> {
    const created = await repository.createOnly(caseValue)
    await refresh()
    return created
  }

  async function getReceipt(commandId: string): Promise<ExecutionReceipt | null> {
    return await repository.getReceipt(commandId)
  }

  async function applyWithReceipt(caseValue: CaseV2, receipt: ExecutionReceipt): Promise<CaseV2> {
    const applied = await repository.applyWithReceipt(caseValue, receipt)
    await refresh()
    return applied
  }

  async function remove(caseId: string): Promise<void> {
    await repository.delete(caseId)
    await refresh()
  }

  return {
    cases: readonly(cases),
    refresh,
    get,
    put,
    createOnly,
    getReceipt,
    applyWithReceipt,
    remove,
  }
}
