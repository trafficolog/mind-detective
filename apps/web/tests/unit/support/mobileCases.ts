import { apply_command, create_case_with_kind } from '../../../app/generated/localExecution'
import type { CaseV2 } from '../../../app/lib/api/contracts'

/** Builds canonical Case v2 fixtures through the generated kernel, never by hand. */
export class CaseBuilder {
  private tick = 0
  constructor(public value: CaseV2) {}

  static create(label = 'Ключи', kind: 'physical' | 'digital' = 'physical', caseId = 'case-1', created = '2026-09-30T10:00:00Z'): CaseBuilder {
    return new CaseBuilder(create_case_with_kind(caseId, label, created, kind) as CaseV2)
  }

  run(commandType: string, payload: Record<string, unknown> = {}): CaseBuilder {
    this.tick += 1
    const minute = String(this.tick).padStart(2, '0')
    const date = this.value.created_at.slice(0, 10)
    this.value = apply_command(structuredClone(this.value) as unknown as Record<string, unknown>, {
      command_id: `cmd-${this.value.case_id}-${this.tick}`,
      expected_updated_at: this.value.updated_at,
      command_type: commandType,
      now: `${date}T11:${minute}:00Z`,
      payload,
    }) as CaseV2
    return this
  }

  search(): CaseBuilder { return this.run('set_mode', { mode: 'search' }) }
  reconstruction(): CaseBuilder { return this.run('set_mode', { mode: 'reconstruction' }) }
  freeAccount(text = 'Вышел из офиса.'): CaseBuilder { return this.run('record_free_account', { entry_id: `fa-${this.tick}`, text }) }
  statement(type: string, text: string, time: string | null = null, limitations: string[] = []): CaseBuilder {
    return this.run('add_statement', {
      statement_id: `st-${this.tick}`, source: 'user', statement_type: type, original_text: text,
      event_time: time, user_confirmation: true, supporting_evidence_ids: [], limitations,
    })
  }

  events(list: Array<[string, 'exact' | 'approximate' | 'unknown', string | null]>): CaseBuilder {
    return this.run('rebuild_timeline', {
      events: list.map(([label, precision, time], index) => ({
        id: `ev-${index}`, label, statement_ids: [], event_time: time, time_precision: precision,
      })),
      last_supported_interaction_id: null,
      first_noticed_missing_id: null,
    })
  }

  target(name: string): CaseBuilder { return this.run('add_search_target', { statement_id: `t-${this.tick}`, target: name }) }
  check(target: string, method: string, result: 'not_found' | 'partial' | 'found' = 'not_found'): CaseBuilder {
    const candidate = this.value.candidates.find(item => item.target.toLowerCase() === target.toLowerCase())
    return this.run('record_search_check', {
      check_id: `chk-${this.tick}`, target, method, result, based_on: candidate ? [candidate.id] : [],
    })
  }
}
