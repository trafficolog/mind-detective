import type { CaseV2 } from '../api/contracts'

export async function exportCase(caseValue: CaseV2): Promise<Blob> {
  return new Blob([`${JSON.stringify(caseValue, null, 2)}\n`], { type: 'application/json' })
}

export async function importCase(
  file: File,
  validate: (payload: unknown) => Promise<CaseV2>,
): Promise<CaseV2> {
  let payload: unknown
  try {
    payload = JSON.parse(await file.text()) as unknown
  } catch {
    throw new Error('MD_WEB_IMPORT_JSON')
  }
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error('MD_WEB_IMPORT_SCHEMA')
  }
  return await validate(payload)
}
