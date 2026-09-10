import { readonly, ref, toRaw, type DeepReadonly, type Ref } from 'vue'
import type { CaseV2, CommandEnvelope } from '~/lib/api/contracts'
import type { CaseApi } from './useCaseApi'

export type PendingCommandStatus = 'queued' | 'pending' | 'failed' | 'succeeded'

export interface PendingCommand extends CommandEnvelope {
  case_id: string
  status: PendingCommandStatus
  attempt_count: number
  error_code: string | null
}

interface CaseSink {
  put(caseValue: CaseV2): Promise<void>
}

interface QueueRecord {
  visible: PendingCommand
  caseSnapshot: CaseV2
  envelope: CommandEnvelope
}

interface ScheduledCommand {
  record: QueueRecord
  resolve: (value: CaseV2) => void
  reject: (reason?: unknown) => void
}

export interface CommandQueue {
  commands: DeepReadonly<Ref<PendingCommand[]>>
  enqueue(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2>
  retry(commandId: string): Promise<CaseV2>
}

function cloneCase(caseValue: CaseV2): CaseV2 {
  return structuredClone(toRaw(caseValue))
}

function cloneEnvelope(command: CommandEnvelope): CommandEnvelope {
  return structuredClone(toRaw(command))
}

function errorCode(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'data' in error) {
    const data = (error as { data?: unknown }).data
    if (typeof data === 'object' && data !== null && 'code' in data) {
      const code = (data as { code?: unknown }).code
      if (typeof code === 'string') return code
    }
  }
  return 'MD_WEB_COMMAND_FAILED'
}

export function makeCommandQueue(api: Pick<CaseApi, 'sendCommand'>, repository: CaseSink): CommandQueue {
  const commands = ref<PendingCommand[]>([])
  const records = new Map<string, QueueRecord>()
  const waiting: ScheduledCommand[] = []
  let running = false

  function refreshVisible(): void {
    commands.value = Array.from(records.values(), ({ visible }) => ({ ...visible }))
  }

  async function execute(record: QueueRecord): Promise<CaseV2> {
    record.visible.status = 'pending'
    record.visible.attempt_count += 1
    record.visible.error_code = null
    refreshVisible()
    try {
      const returnedCase = await api.sendCommand(cloneCase(record.caseSnapshot), cloneEnvelope(record.envelope))
      await repository.put(returnedCase)
      record.visible.status = 'succeeded'
      refreshVisible()
      return returnedCase
    } catch (error: unknown) {
      record.visible.status = 'failed'
      record.visible.error_code = errorCode(error)
      refreshVisible()
      throw error
    }
  }

  function startNext(): void {
    if (running) return
    const scheduled = waiting.shift()
    if (!scheduled) return

    running = true
    execute(scheduled.record)
      .then(scheduled.resolve, scheduled.reject)
      .finally(() => {
        running = false
        startNext()
      })
  }

  function schedule(record: QueueRecord): Promise<CaseV2> {
    const result = new Promise<CaseV2>((resolve, reject) => {
      waiting.push({ record, resolve, reject })
    })
    startNext()
    return result
  }

  function enqueue(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2> {
    if (records.has(command.command_id)) {
      return Promise.reject(new Error(`MD_WEB_DUPLICATE_COMMAND_ID:${command.command_id}`))
    }
    const visible: PendingCommand = {
      ...cloneEnvelope(command),
      case_id: caseValue.case_id,
      status: 'queued',
      attempt_count: 0,
      error_code: null,
    }
    const record: QueueRecord = {
      visible,
      caseSnapshot: cloneCase(caseValue),
      envelope: cloneEnvelope(command),
    }
    records.set(command.command_id, record)
    refreshVisible()
    return schedule(record)
  }

  function retry(commandId: string): Promise<CaseV2> {
    const record = records.get(commandId)
    if (!record) return Promise.reject(new Error(`MD_WEB_COMMAND_NOT_FOUND:${commandId}`))
    if (record.visible.status !== 'failed') {
      return Promise.reject(new Error(`MD_WEB_COMMAND_NOT_RETRYABLE:${commandId}`))
    }
    return schedule(record)
  }

  return { commands: readonly(commands), enqueue, retry }
}

export function useCommandQueue(): CommandQueue {
  const api = useCaseApi()
  const repository = useCaseRepository()
  return makeCommandQueue(api, repository)
}
