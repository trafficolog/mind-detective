import type { CaseV2, ExperimentalArm, ProposalResponse } from '~/lib/api/contracts'
import { EXECUTION_IDENTITY } from '~/lib/api/executionContract'

export interface CaseApi {
  nextProposal(
    caseValue: CaseV2,
    requestId: string,
    now: string,
    mode: 'reconstruction' | 'search',
    locale: 'ru' | 'en',
    experimentalArm: ExperimentalArm,
  ): Promise<ProposalResponse>
}

export function isCaseApiTransportError(error: unknown): boolean {
  if (!(error instanceof Error) || error.name !== 'FetchError') return false
  return (error as Error & { response?: unknown }).response == null
}

export function caseApiErrorCode(error: unknown): string | null {
  if (!error || typeof error !== 'object') return null
  const candidate = error as {
    data?: { code?: unknown }
    response?: { _data?: { code?: unknown } }
  }
  const code = candidate.data?.code ?? candidate.response?._data?.code
  return typeof code === 'string' ? code : null
}

export function useCaseApi(): CaseApi {
  const config = useRuntimeConfig()
  const baseURL = String(config.public.mindDetectiveApiBase || 'http://127.0.0.1:8000')

  async function nextProposal(
    caseValue: CaseV2,
    requestId: string,
    now: string,
    mode: 'reconstruction' | 'search',
    locale: 'ru' | 'en',
    experimentalArm: ExperimentalArm,
  ): Promise<ProposalResponse> {
    return await $fetch<ProposalResponse>('/api/v1/proposal/next', {
      baseURL,
      method: 'POST',
      body: {
        request_id: requestId,
        now,
        case: caseValue,
        mode,
        locale,
        experimental_arm: experimentalArm,
        execution_identity: EXECUTION_IDENTITY,
      },
    })
  }

  return { nextProposal }
}