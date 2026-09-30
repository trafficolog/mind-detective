import { describe, expect, it } from 'vitest'
import { maskClockInput, parseClock } from '../../app/lib/mobile/timeMask'

describe('ЧЧ:ММ time mask', () => {
  it('inserts the colon automatically and keeps at most four digits', () => {
    expect(maskClockInput('0')).toBe('0')
    expect(maskClockInput('08')).toBe('08')
    expect(maskClockInput('080')).toBe('08:0')
    expect(maskClockInput('0800')).toBe('08:00')
    expect(maskClockInput('08:005')).toBe('08:00')
    expect(maskClockInput('a1b2c3')).toBe('12:3')
  })

  it('T06 parses valid clock times and rejects impossible ones', () => {
    expect(parseClock('08:00')).toBe('08:00')
    expect(parseClock('9:30')).toBe('09:30')
    expect(parseClock('23.59')).toBe('23:59')
    expect(parseClock('25:99')).toBeNull()
    expect(parseClock('24:00')).toBeNull()
    expect(parseClock('08:0')).toBeNull()
    expect(parseClock('')).toBeNull()
  })
})
