import type { CaseV2, CommandEnvelope, ExperimentalArm, ProposalResponse } from '~/lib/api/contracts'
import { EXECUTION_IDENTITY } from '~/lib/api/executionContract'

export interface CaseApi {
  createCase(caseId: string, itemLabel: string, now: string): Promise<CaseV2>
  validateCase(caseValue: Record<string, unknown>): Promise<CaseV2>
  sendCommand(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2>
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

  async function createCase(caseId: string, itemLabel: string, now: string): Promise<CaseV2> {
    const response = await $fetch<{ case: CaseV2 }>('/api/v1/case/create', {
      baseURL,
      method: 'POST',
      body: { case_id: caseId, item_label: itemLabel, now },
    })
    return response.case
  }

  async function validateCase(caseValue: Record<string, unknown>): Promise<CaseV2> {
    const response = await $fetch<{ case: CaseV2 }>('/api/v1/case/validate', {
      baseURL,
      method: 'POST',
      body: { case: caseValue },
    })
    return response.case
  }

  async function sendCommand(caseValue: CaseV2, command: CommandEnvelope): Promise<CaseV2> {
    const response = await $fetch<{ case: CaseV2 }>('/api/v1/case/command', {
      baseURL,
      method: 'POST',
      body: { case: caseValue, command },
    })
    return response.case
  }

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

  return { createCase, validateCase, sendCommand, nextProposal }
}