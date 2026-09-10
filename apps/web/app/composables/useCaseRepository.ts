import { readonly, type DeepReadonly, type Ref } from 'vue'
import type { CaseV2 } from '~/lib/api/contracts'
import { createIndexedDbCaseRepository } from '~/lib/storage/indexeddb'

const repository = createIndexedDbCaseRepository()

export interface CaseRepositoryComposable {
  cases: DeepReadonly<Ref<CaseV2[]>>
  refresh(): Promise<CaseV2[]>
  get(caseId: string): Promise<CaseV2 | null>
  put(caseValue: CaseV2): Promise<void>
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

  async function remove(caseId: string): Promise<void> {
    await repository.delete(caseId)
    await refresh()
  }

  return {
    cases: readonly(cases),
    refresh,
    get,
    put,
    remove,
  }
}
