import { toRaw } from 'vue'
import type { CaseV2, CommandEnvelope } from '~/lib/api/contracts'
import { errorCodeOf, errorMessage } from '~/lib/mobile/commands'
import { caseNumbers, itemKind } from '~/lib/mobile/viewModel'
import type { ItemKind } from '~/lib/mobile/vocab'

/** Mobile shell access to canonical cases. Every mutation goes through the generated local executor. */
export function useMobileCases() {
  const repository = useCaseRepository()
  const localExecution = useLocalExecution()
  const lastCaseId = useState<string | null>('md-mobile-last-case', () => null)
  const loaded = useState<boolean>('md-mobile-cases-loaded', () => false)

  const cases = computed(() => repository.cases.value as CaseV2[])
  const numbers = computed(() => caseNumbers(cases.value))

  async function ensureLoaded(): Promise<void> {
    if (loaded.value) return
    await repository.refresh()
    loaded.value = true
  }

  async function get(caseId: string): Promise<CaseV2 | null> {
    return await repository.get(caseId)
  }

  async function create(label: string, kind: ItemKind, mode: 'reconstruction' | 'search'): Promise<CaseV2> {
    const created = await localExecution.createMobileCase(globalThis.crypto.randomUUID(), label.trim(), new Date().toISOString(), kind, mode)
    await repository.refresh()
    lastCaseId.value = created.case_id
    return created
  }

  async function run(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2> {
    return await localExecution.sendCommand(structuredClone(toRaw(caseValue)), command)
  }

  async function put(caseValue: CaseV2): Promise<void> {
    await repository.put(caseValue)
  }

  async function remove(caseId: string): Promise<void> {
    await repository.remove(caseId)
    if (lastCaseId.value === caseId) lastCaseId.value = null
  }

  async function removeAll(): Promise<void> {
    for (const caseValue of [...cases.value]) await repository.remove(caseValue.case_id)
    lastCaseId.value = null
  }

  function messageFor(error: unknown, caseValue?: CaseV2 | null): string {
    return errorMessage(errorCodeOf(error), caseValue ? itemKind(caseValue) : 'physical')
  }

  return { cases, numbers, lastCaseId, ensureLoaded, get, create, run, put, remove, removeAll, messageFor }
}
