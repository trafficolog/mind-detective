/** Input mask ЧЧ:ММ: digits only, at most four, colon inserted automatically. */
export function maskClockInput(raw: string): string {
  const digits = raw.replace(/\D/g, '').slice(0, 4)
  return digits.length > 2 ? `${digits.slice(0, 2)}:${digits.slice(2)}` : digits
}

/** Parses a clock time and normalises it to ЧЧ:ММ; returns null when impossible. */
export function parseClock(value: string): string | null {
  const match = /^([01]?\d|2[0-3])[:.]([0-5]\d)$/.exec(String(value ?? '').trim())
  if (!match) return null
  return `${match[1]!.padStart(2, '0')}:${match[2]}`
}
