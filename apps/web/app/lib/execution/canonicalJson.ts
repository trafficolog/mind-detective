const ERROR = 'MD_LOCAL_CANONICAL_JSON'

function comparePythonStrings(left: string, right: string): number {
  const leftPoints = Array.from(left, char => char.codePointAt(0) ?? 0)
  const rightPoints = Array.from(right, char => char.codePointAt(0) ?? 0)
  const limit = Math.min(leftPoints.length, rightPoints.length)
  for (let index = 0; index < limit; index += 1) {
    if (leftPoints[index]! < rightPoints[index]!) return -1
    if (leftPoints[index]! > rightPoints[index]!) return 1
  }
  if (leftPoints.length < rightPoints.length) return -1
  if (leftPoints.length > rightPoints.length) return 1
  return 0
}

function encodeString(value: string): string {
  const encoded = JSON.stringify(value)
  if (encoded === undefined) throw new Error(`${ERROR}: unsupported string`)
  return encoded
}

export function canonicalJson(value: unknown): string {
  if (value === null) return 'null'
  if (typeof value === 'string') return encodeString(value)
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) throw new Error(`${ERROR}: only safe integers are supported`)
    return JSON.stringify(Object.is(value, -0) ? 0 : value)
  }
  if (Array.isArray(value)) {
    return `[${value.map(item => canonicalJson(item)).join(',')}]`
  }
  if (typeof value === 'object') {
    const prototype = Object.getPrototypeOf(value)
    if (prototype !== Object.prototype && prototype !== null) {
      throw new Error(`${ERROR}: unsupported object prototype`)
    }
    const object = value as Record<string, unknown>
    const keys = Object.keys(object).sort(comparePythonStrings)
    const parts = keys.map(key => `${encodeString(key)}:${canonicalJson(object[key])}`)
    return `{${parts.join(',')}}`
  }
  throw new Error(`${ERROR}: unsupported value type ${typeof value}`)
}

export async function canonicalSha256(value: unknown): Promise<string> {
  const data = new TextEncoder().encode(canonicalJson(value))
  const digest = await crypto.subtle.digest('SHA-256', data)
  const hex = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('')
  return `sha256:${hex}`
}
