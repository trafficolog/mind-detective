import { reactive } from 'vue'
import { describe, expect, it } from 'vitest'
import { makeCommandQueue } from '../../app/composables/useCommandQueue'
import type { CaseV2, CommandEnvelope } from '../../app/lib/api/contracts'

function caseFixture(updatedAt = '2026-09-10T07:00:00Z'): CaseV2 {
  return {
    schema: 'mind-detective-case/v2',
    case_id: 'case-1',
    item_label: 'ключи',
    created_at: '2026-09-10T07:00:00Z',
    updated_at: updatedAt,
    lifecycle: 'active',
    statements: [],
    timeline: null,
    search_checks: [],
    candidates: [],
    next_action: null,
    constraints: [],
    outcome: null,
    current_mode: 'search',
    interaction_journal: [],
    action_feedback: [],
  }
}

function command(id: string): CommandEnvelope {
  return {
    command_id: id,
    expected_updated_at: '2026-09-10T07:00:00Z',
    command_type: 'record_search_check',
    now: '2026-09-10T07:01:00Z',
    payload: { check_id: `check-${id}`, target: 'рюкзак', result: 'not_found' },
  }
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

describe('transport-only command queue', () => {
  it('does not mutate canonical storage while a request is pending', async () => {
    const gate = deferred<CaseV2>()
    const writes: CaseV2[] = []
    const api = { sendCommand: async () => await gate.promise }
    const repository = { put: async (value: CaseV2) => { writes.push(structuredClone(value)) } }
    const queue = makeCommandQueue(api, repository)
    const original = caseFixture()

    const pending = queue.enqueue(original, command('cmd-1'))
    await Promise.resolve()
    expect(writes).toEqual([])
    expect(original.updated_at).toBe('2026-09-10T07:00:00Z')
    expect(queue.commands.value[0]?.status).toBe('pending')

    const returned = caseFixture('2026-09-10T07:01:00Z')
    gate.resolve(returned)
    await expect(pending).resolves.toEqual(returned)
    expect(writes).toEqual([returned])
  })

  it('accepts reactive case values from Vue refs', async () => {
    const started: string[] = []
    const api = {
      sendCommand: async (_caseValue: CaseV2, envelope: CommandEnvelope) => {
        started.push(envelope.command_id)
        return caseFixture('2026-09-10T07:01:00Z')
      },
    }
    const repository = { put: async (_value: CaseV2) => undefined }
    const queue = makeCommandQueue(api, repository)
    const reactiveCase = reactive(caseFixture()) as CaseV2

    await expect(queue.enqueue(reactiveCase, command('cmd-reactive'))).resolves.toMatchObject({
      updated_at: '2026-09-10T07:01:00Z',
    })
    expect(started).toEqual(['cmd-reactive'])
  })

  it('sends commands sequentially', async () => {
    const first = deferred<CaseV2>()
    const second = deferred<CaseV2>()
    const started: string[] = []
    const api = {
      sendCommand: async (_caseValue: CaseV2, envelope: CommandEnvelope) => {
        started.push(envelope.command_id)
        return envelope.command_id === 'cmd-1' ? await first.promise : await second.promise
      },
    }
    const repository = { put: async (_value: CaseV2) => undefined }
    const queue = makeCommandQueue(api, repository)

    const one = queue.enqueue(caseFixture(), command('cmd-1'))
    const two = queue.enqueue(caseFixture(), command('cmd-2'))
    await Promise.resolve()
    expect(started).toEqual(['cmd-1'])

    first.resolve(caseFixture('2026-09-10T07:01:00Z'))
    await one
    await Promise.resolve()
    expect(started).toEqual(['cmd-1', 'cmd-2'])
    second.resolve(caseFixture('2026-09-10T07:02:00Z'))
    await two
  })

  it('retries byte-equivalent case snapshot and envelope after failure', async () => {
    const calls: string[] = []
    let attempt = 0
    const api = {
      sendCommand: async (caseValue: CaseV2, envelope: CommandEnvelope) => {
        calls.push(JSON.stringify({ case: caseValue, command: envelope }))
        attempt += 1
        if (attempt === 1) throw new Error('offline')
        return caseFixture('2026-09-10T07:01:00Z')
      },
    }
    const writes: CaseV2[] = []
    const repository = { put: async (value: CaseV2) => { writes.push(value) } }
    const queue = makeCommandQueue(api, repository)

    await expect(queue.enqueue(caseFixture(), command('cmd-1'))).rejects.toThrow('offline')
    expect(writes).toEqual([])
    expect(queue.commands.value[0]?.status).toBe('failed')

    await expect(queue.retry('cmd-1')).resolves.toMatchObject({ updated_at: '2026-09-10T07:01:00Z' })
    expect(calls).toHaveLength(2)
    expect(calls[1]).toBe(calls[0])
    expect(queue.commands.value[0]?.attempt_count).toBe(2)
  })
})
