import { describe, expect, it } from 'vitest'
import { isCaseApiTransportError } from '../../app/composables/useCaseApi'

describe('case API failure classification', () => {
  it('treats a response-less FetchError as a transport failure', () => {
    const error = Object.assign(new Error('fetch failed'), {
      name: 'FetchError',
      response: undefined,
    })

    expect(isCaseApiTransportError(error)).toBe(true)
  })

  it('does not treat an HTTP response as a transport failure', () => {
    const error = Object.assign(new Error('request failed'), {
      name: 'FetchError',
      response: { status: 409 },
      statusCode: 409,
    })

    expect(isCaseApiTransportError(error)).toBe(false)
  })

  it('does not hide unrelated application errors behind offline fallback', () => {
    expect(isCaseApiTransportError(new Error('bug'))).toBe(false)
  })
})
