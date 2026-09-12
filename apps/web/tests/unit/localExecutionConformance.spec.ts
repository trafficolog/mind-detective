import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  PortableKernelError,
  apply_command,
  build_checklist_proposal_json,
  create_case,
  select_next_action_json,
} from '../../app/generated/localExecution'

type Expected = { result: unknown } | { error_code: string }

type CorpusVector = {
  id: string
  operation: 'create_case' | 'command' | 'proposal' | 'planner'
  input: Record<string, unknown>
  expected: Expected
}

const corpusPath = resolve(process.cwd(), '../../conformance/local-execution/v1/vectors.json')
const vectors = JSON.parse(readFileSync(corpusPath, 'utf8')) as CorpusVector[]

const requiredReconstructionVectorIds = [
  'reconstruction_record_free_account',
  'reconstruction_statement_requires_free_account',
  'reconstruction_rebuild_timeline_unknowns',
  'reconstruction_rebuild_timeline_contradiction',
  'reconstruction_transition_to_search_preserves_evidence',
] as const

function execute(vector: CorpusVector): Expected {
  try {
    if (vector.operation === 'create_case') {
      return {
        result: create_case(
          String(vector.input.case_id),
          String(vector.input.item_label),
          String(vector.input.now),
        ),
      }
    }
    if (vector.operation === 'command') {
      return {
        result: apply_command(
          vector.input.case as Record<string, unknown>,
          vector.input.command as Record<string, unknown>,
        ),
      }
    }
    if (vector.operation === 'proposal') {
      return {
        result: build_checklist_proposal_json(
          vector.input.case as Record<string, unknown>,
          String(vector.input.mode),
        ),
      }
    }
    return {
      result: select_next_action_json(vector.input.candidates as unknown[]),
    }
  } catch (error: unknown) {
    if (error instanceof PortableKernelError) {
      return { error_code: error.code }
    }
    throw error
  }
}

describe('generated local execution differential conformance', () => {
  it('contains a non-trivial committed corpus', () => {
    expect(vectors.length).toBeGreaterThanOrEqual(50)
  })

  it('contains the required reconstruction vectors', () => {
    const ids = new Set(vectors.map((vector) => vector.id))
    for (const vectorId of requiredReconstructionVectorIds) {
      expect(ids.has(vectorId)).toBe(true)
    }
  })

  it('matches every committed conformance vector', () => {
    for (const vector of vectors) {
      expect(execute(vector)).toEqual(vector.expected)
    }
  })

  for (const vector of vectors) {
    it(vector.id, () => {
      expect(execute(vector)).toEqual(vector.expected)
    })
  }
})
