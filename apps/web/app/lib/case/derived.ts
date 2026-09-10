import type { CaseV2, SearchCheckV2 } from '../api/contracts'

export interface ProgressSummary {
  checked: number
  remaining: number
  inaccessible: number
}

export interface PriorCheckAnnotation {
  check_id: string
  method: SearchCheckV2['method']
  result: SearchCheckV2['result']
  inaccessible_parts: string[]
  completed_at: string | null
}

export function deriveProgress(caseValue: CaseV2): ProgressSummary {
  const candidateIds = new Set(caseValue.candidates.map(candidate => candidate.id))
  const latestChecks = new Map<string, SearchCheckV2>()

  for (const check of caseValue.search_checks) {
    for (const candidateId of check.based_on) {
      if (candidateIds.has(candidateId)) {
        latestChecks.set(candidateId, check)
      }
    }
  }

  const inaccessibleIds = new Set<string>()
  for (const [candidateId, check] of latestChecks) {
    if (check.result === 'inaccessible' || check.inaccessible_parts.length > 0) {
      inaccessibleIds.add(candidateId)
    }
  }

  let checked = 0
  let remaining = 0
  for (const candidate of caseValue.candidates) {
    if (inaccessibleIds.has(candidate.id)) {
      continue
    }
    if (candidate.check_state === 'checked') {
      checked += 1
    } else {
      remaining += 1
    }
  }

  return {
    checked,
    remaining,
    inaccessible: inaccessibleIds.size,
  }
}

export function derivePriorCheckAnnotation(
  caseValue: CaseV2,
  candidateId: string,
): PriorCheckAnnotation | null {
  const check = [...caseValue.search_checks]
    .reverse()
    .find(item => item.based_on.includes(candidateId))
  if (!check) {
    return null
  }
  return {
    check_id: check.id,
    method: check.method,
    result: check.result,
    inaccessible_parts: [...check.inaccessible_parts],
    completed_at: check.completed_at,
  }
}
