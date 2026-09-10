import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { canonicalJson, canonicalSha256 } from '~/lib/execution/canonicalJson'

interface Vector {
  name: string
  value: unknown
  canonical: string
  sha256: string
}

const fixturePath = fileURLToPath(
  new URL('../../../../tests/fixtures/local-execution-canonical-json-v1.json', import.meta.url),
)
const vectors = JSON.parse(readFileSync(fixturePath, 'utf8')) as Vector[]

describe('local execution canonical JSON', () => {
  it('matches every Python-owned canonical vector and digest', async () => {
    for (const vector of vectors) {
      expect(canonicalJson(vector.value), vector.name).toBe(vector.canonical)
      await expect(canonicalSha256(vector.value), vector.name).resolves.toBe(vector.sha256)
    }
  })

  it('does not use JSON.stringify object ordering as the canonical object algorithm', () => {
    expect(canonicalJson({ 10: 'ten', 2: 'two', '01': 'leading', a: 1 }))
      .toBe('{"01":"leading","10":"ten","2":"two","a":1}')
  })

  it('fails closed for floating or unsupported values', () => {
    expect(() => canonicalJson({ x: 1.25 })).toThrow('MD_LOCAL_CANONICAL_JSON')
    expect(() => canonicalJson({ x: Number.NaN })).toThrow('MD_LOCAL_CANONICAL_JSON')
    expect(() => canonicalJson({ x: undefined })).toThrow('MD_LOCAL_CANONICAL_JSON')
  })
})
