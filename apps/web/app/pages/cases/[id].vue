<script setup lang="ts">
import { shallowRef, toRaw } from 'vue'
import { caseApiErrorCode, isCaseApiTransportError } from '~/composables/useCaseApi'
import type { ActionFeedbackV2, CaseV2, CommandEnvelope, ProposalModel, SearchMethod } from '~/lib/api/contracts'
import { EXECUTION_CONTRACT_MISMATCH } from '~/lib/api/executionContract'
import { derivePriorCheckAnnotation } from '~/lib/case/derived'
import type { EvalEventName } from '~/lib/eval/contracts'
import { appendEvalEvent } from '~/lib/eval/log'
import { finishEvaluationSession } from '~/lib/eval/store'

type FoundContext = 'current_suggested_action' | 'elsewhere_unplanned' | 'after_previous_check' | 'unknown'
type RefinedMethod = Exclude<SearchMethod, 'reported_check' | 'inaccessible'>
type RetryableCommand = { caseSnapshot: CaseV2; command: CommandEnvelope }

const route = useRoute()
const repository = useCaseRepository()
const api = useCaseApi()
const arm = useExperimentalArm()
const evaluation = useEvaluationSession()
const localExecution = useLocalExecution()
const { locale, t } = useCopy()

const caseValue = ref<CaseV2 | null>(null)
const proposal = ref<ProposalModel | null>(null)
const currentProposalId = ref<string | null>(null)
const loading = ref(true)
const busy = ref(false)
const errorCode = ref<string | null>(null)
const guardCode = ref<string | null>(null)
const assistantOfflineFallback = ref(false)
const showReject = ref(false)
const showClose = ref(false)
const suppressedQualityCheckId = ref<string | null>(null)
const retryCommandState = shallowRef<RetryableCommand | null>(null)

const caseId = computed(() => String(route.params.id || ''))
const evaluationSession = computed(() => evaluation.session.value)
const executionContractMismatch = computed(() => errorCode.value === EXECUTION_CONTRACT_MISMATCH)
const safetyErrorCode = computed(() => errorCode.value?.startsWith('MD_SAFE_') ? errorCode.value : null)
const engaged = computed(() => {
  const current = caseValue.value
  if (!current) return false
  return current.current_mode !== 'unselected'
    || current.statements.length > 0
    || current.search_checks.length > 0
    || current.interaction_journal.length > 0
})
const qualityContext = computed(() => {
  const current = caseValue.value
  const candidateId = proposal.value?.candidate_id
  if (!current || proposal.value?.kind !== 'next_action' || !candidateId) return null
  const prior = derivePriorCheckAnnotation(current, candidateId)
  if (!prior || prior.method !== 'reported_check' || prior.check_id === suppressedQualityCheckId.value) return null
  return { ...prior, target: proposal.value.target ?? current.candidates.find(candidate => candidate.id === candidateId)?.target ?? '' }
})

watch(
  () => proposal.value?.candidate_id ?? null,
  (nextCandidateId, previousCandidateId) => {
    if (nextCandidateId !== previousCandidateId) suppressedQualityCheckId.value = null
  },
)

async function logEvaluationEvent(event: EvalEventName, metadata: Record<string, unknown> = {}): Promise<void> {
  const session = evaluation.session.value
  if (!session || session.outcome !== null || session.case_id !== caseId.value) return
  try {
    await appendEvalEvent(session.evaluation_session_id, event, metadata)
  } catch {
    // Evaluation storage must never block canonical Case progress.
  }
}

function linkedMetadata(
  current: CaseV2,
  candidateId: string | null | undefined,
  proposalId: string | null,
): Record<string, unknown> {
  const metadata: Record<string, unknown> = {
    case_id: current.case_id,
    mode: current.current_mode,
  }
  if (candidateId) metadata.candidate_id = candidateId
  if (proposalId) metadata.proposal_id = proposalId
  return metadata
}

async function trackProposal(current: CaseV2, next: ProposalModel): Promise<void> {
  proposal.value = next
  if (next.kind !== 'next_action') {
    currentProposalId.value = null
    return
  }
  const proposalId = crypto.randomUUID()
  currentProposalId.value = proposalId
  await logEvaluationEvent('next_action_shown', linkedMetadata(current, next.candidate_id, proposalId))
}

function snapshotCase(current: CaseV2): CaseV2 {
  return structuredClone(toRaw(current))
}

function executionErrorCode(error: unknown, fallback: string): string {
  if (error && typeof error === 'object' && 'code' in error && typeof error.code === 'string') {
    return error.code
  }
  return error instanceof Error ? error.message : fallback
}

function envelope(commandType: CommandEnvelope['command_type'], payload: Record<string, unknown>): CommandEnvelope {
  if (!caseValue.value) throw new Error('MD_WEB_CASE_NOT_LOADED')
  return {
    command_id: crypto.randomUUID(),
    expected_updated_at: caseValue.value.updated_at,
    command_type: commandType,
    now: new Date().toISOString(),
    payload,
  }
}

async function setLocalProposal(current: CaseV2): Promise<void> {
  if (current.current_mode !== 'search') {
    proposal.value = null
    currentProposalId.value = null
    guardCode.value = null
    return
  }
  const next = localExecution.checklistProposal(current)
  await trackProposal(current, next)
  guardCode.value = null
}

async function useAssistantFallback(current: CaseV2, reasonCode: 'offline' | 'transport_error'): Promise<void> {
  assistantOfflineFallback.value = true
  await logEvaluationEvent('assistant_offline_fallback', {
    case_id: current.case_id,
    reason_code: reasonCode,
  })
  await setLocalProposal(current)
}

async function refreshProposal(): Promise<void> {
  const current = caseValue.value
  assistantOfflineFallback.value = false
  if (!current || current.lifecycle !== 'active' || current.current_mode !== 'search') {
    proposal.value = null
    currentProposalId.value = null
    guardCode.value = null
    return
  }

  if (arm.value === 'checklist') {
    await setLocalProposal(current)
    return
  }

  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    await useAssistantFallback(current, 'offline')
    return
  }

  try {
    const response = await api.nextProposal(
      current,
      crypto.randomUUID(),
      new Date().toISOString(),
      'search',
      locale.value,
      arm.value,
    )
    if (response.case.updated_at !== current.updated_at || response.case.interaction_journal.length !== current.interaction_journal.length) {
      await repository.put(response.case)
      caseValue.value = response.case
    }
    await trackProposal(response.case, response.proposal)
    guardCode.value = response.guard_code
    if (response.guard_code) {
      await logEvaluationEvent('ai_guard_blocked', {
        case_id: response.case.case_id,
        guard_code: response.guard_code,
      })
    }
  } catch (error: unknown) {
    if ((typeof navigator !== 'undefined' && !navigator.onLine) || isCaseApiTransportError(error)) {
      await useAssistantFallback(current, typeof navigator !== 'undefined' && !navigator.onLine ? 'offline' : 'transport_error')
      return
    }
    const apiCode = caseApiErrorCode(error)
    if (apiCode === EXECUTION_CONTRACT_MISMATCH) {
      errorCode.value = apiCode
      proposal.value = null
      currentProposalId.value = null
      guardCode.value = null
      return
    }
    errorCode.value = 'MD_WEB_PROPOSAL_FAILED'
    proposal.value = null
    currentProposalId.value = null
  }
}

async function runCommand(
  command: CommandEnvelope,
  retryCaseSnapshot?: CaseV2,
  refreshAfter = true,
): Promise<CaseV2 | null> {
  const current = caseValue.value
  if (!current) return null
  const inputCase = retryCaseSnapshot ? snapshotCase(retryCaseSnapshot) : snapshotCase(current)
  busy.value = true
  errorCode.value = null
  try {
    const returned = await localExecution.sendCommand(inputCase, command)
    retryCommandState.value = null
    caseValue.value = returned
    if (refreshAfter) await refreshProposal()
    return returned
  } catch (error: unknown) {
    const code = executionErrorCode(error, 'MD_WEB_LOCAL_EXECUTION_FAILED')
    const normalizedCode = code.startsWith('MD_') ? code : 'MD_WEB_LOCAL_EXECUTION_FAILED'
    errorCode.value = normalizedCode
    if (normalizedCode.startsWith('MD_SAFE_')) {
      retryCommandState.value = null
      proposal.value = null
      currentProposalId.value = null
      guardCode.value = null
      return null
    }
    if (normalizedCode === 'MD_WEB_LOCAL_EXECUTION_FAILED' || normalizedCode.startsWith('MD_WEB_IDB_')) {
      retryCommandState.value = {
        caseSnapshot: structuredClone(inputCase),
        command: structuredClone(command),
      }
    } else {
      retryCommandState.value = null
    }
    await logEvaluationEvent('local_execution_failed', {
      case_id: current.case_id,
      command_id: command.command_id,
      outcome_code: normalizedCode,
    })
    return null
  } finally {
    busy.value = false
  }
}

async function retryLastCommand(): Promise<void> {
  const retry = retryCommandState.value
  if (!retry) return
  await runCommand(retry.command, retry.caseSnapshot)
}

async function resumeAfterSafety(): Promise<void> {
  errorCode.value = null
  const current = caseValue.value
  if (current?.lifecycle === 'active' && current.current_mode === 'search') await refreshProposal()
}

async function switchToSearch(): Promise<void> {
  await runCommand(envelope('set_mode', { mode: 'search' }))
}

async function pauseCase(): Promise<void> {
  const returned = await runCommand(envelope('pause', {}))
  if (returned) await logEvaluationEvent('pause', { case_id: returned.case_id })
}

async function resumeCase(): Promise<void> {
  const returned = await runCommand(envelope('resume', {}))
  if (returned) await logEvaluationEvent('resume', { case_id: returned.case_id })
}

async function addSearchTarget(target: string): Promise<void> {
  const current = caseValue.value
  const normalizedTarget = target.trim()
  if (!current || current.current_mode !== 'search' || !normalizedTarget) return

  await runCommand(envelope('add_statement', {
    statement_id: crypto.randomUUID(),
    source: 'user',
    statement_type: 'search_suggestion',
    original_text: normalizedTarget,
    event_time: null,
    user_confirmation: true,
    supporting_evidence_ids: [],
    limitations: [],
  }))
}

async function markChecked(): Promise<void> {
  const action = proposal.value
  const current = caseValue.value
  if (!action?.target || !current) return
  const proposalId = currentProposalId.value
  const candidateId = action.candidate_id
  const duplicate = Boolean(candidateId && current.search_checks.some(check =>
    check.completed_at !== null && check.based_on.includes(candidateId),
  ))
  await logEvaluationEvent('check_started', linkedMetadata(current, candidateId, proposalId))
  const now = new Date().toISOString()
  const checkId = crypto.randomUUID()
  suppressedQualityCheckId.value = checkId
  const returned = await runCommand(envelope('record_search_check', {
    check_id: checkId,
    target: action.target,
    method: 'reported_check',
    started_at: now,
    completed_at: now,
    result: 'not_found',
    inaccessible_parts: [],
    based_on: candidateId ? [candidateId] : [],
    notes: [],
  }), undefined, false)
  if (returned) {
    await logEvaluationEvent('check_finished', linkedMetadata(current, candidateId, proposalId))
    if (duplicate) {
      await logEvaluationEvent('duplicate_check_detected', {
        case_id: returned.case_id,
        ...(candidateId ? { candidate_id: candidateId } : {}),
        ...(proposalId ? { proposal_id: proposalId } : {}),
      })
    }
    await refreshProposal()
  }
}

async function refineQuality(payload: { checkId: string; method: RefinedMethod; inaccessibleParts: string[] }): Promise<void> {
  const candidateId = proposal.value?.candidate_id
  const returned = await runCommand(envelope('refine_search_check', {
    check_id: payload.checkId,
    method: payload.method,
    inaccessible_parts: payload.inaccessibleParts,
  }))
  if (returned) {
    suppressedQualityCheckId.value = payload.checkId
    await logEvaluationEvent('check_quality_clarified', {
      case_id: returned.case_id,
      ...(candidateId ? { candidate_id: candidateId } : {}),
    })
  }
}

async function rejectAction(reason: ActionFeedbackV2['reason']): Promise<void> {
  const current = caseValue.value
  const candidateId = proposal.value?.candidate_id
  const proposalId = currentProposalId.value
  if (!current || !candidateId) return
  const returned = await runCommand(envelope('reject_next_action', {
    feedback_id: crypto.randomUUID(),
    candidate_id: candidateId,
    reason,
  }), undefined, false)
  if (returned) {
    showReject.value = false
    await logEvaluationEvent('next_action_rejected', {
      case_id: returned.case_id,
      candidate_id: candidateId,
      ...(proposalId ? { proposal_id: proposalId } : {}),
      reason_code: reason,
    })
    await refreshProposal()
  }
}

async function closeFound(context: FoundContext): Promise<void> {
  const activeSession = evaluation.session.value
  const returned = await runCommand(envelope('close_found', { outcome: { found_context: context } }))
  if (returned) {
    showClose.value = false
    proposal.value = null
    currentProposalId.value = null
    if (activeSession && activeSession.outcome === null && activeSession.case_id === returned.case_id) {
      evaluation.session.value = await finishEvaluationSession(
        activeSession.evaluation_session_id,
        'found',
        new Date().toISOString(),
        { found_context: context },
      )
    }
  }
}

async function closeUnresolved(): Promise<void> {
  const activeSession = evaluation.session.value
  const returned = await runCommand(envelope('close_unresolved', { outcome: {} }))
  if (returned) {
    showClose.value = false
    proposal.value = null
    currentProposalId.value = null
    if (activeSession && activeSession.outcome === null && activeSession.case_id === returned.case_id) {
      evaluation.session.value = await finishEvaluationSession(
        activeSession.evaluation_session_id,
        'unresolved',
        new Date().toISOString(),
      )
    }
  }
}

function handleDeleted(): void {
  caseValue.value = null
  proposal.value = null
  currentProposalId.value = null
  retryCommandState.value = null
}

function scrollJournal(): void {
  document.querySelector('[data-testid="interaction-journal"]')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(async () => {
  try {
    caseValue.value = await repository.get(caseId.value)
    if (caseValue.value?.lifecycle === 'active') await refreshProposal()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="case-page" data-testid="case-page">
    <p v-if="loading" class="muted" aria-live="polite">{{ t('case.loading') }}</p>
    <section v-else-if="!caseValue" class="hero-panel">
      <h1>{{ t('case.not_found') }}</h1>
      <p class="lede">{{ t('case.not_found_help') }}</p>
      <NuxtLink class="primary-action" to="/">{{ t('case.to_list') }}</NuxtLink>
    </section>

    <template v-else-if="caseValue.lifecycle === 'closed_found' || caseValue.lifecycle === 'closed_unresolved'">
      <CaseOutcome :case-value="caseValue" />
      <EvaluationPostCaseRatings
        v-if="evaluationSession && evaluationSession.case_id === caseValue.case_id && evaluationSession.outcome !== null"
        :evaluation-session-id="evaluationSession.evaluation_session_id"
      />
      <CaseDataActions :case-value="caseValue" :allow-delete="true" @deleted="handleDeleted" />
    </template>

    <template v-else>
      <div v-if="caseValue.lifecycle === 'paused'" class="privacy-note" data-testid="paused-banner">
        {{ t('case.paused_copy') }}
        <button class="primary-action" type="button" :disabled="busy" @click="resumeCase">{{ t('case.resume') }}</button>
      </div>

      <aside
        v-if="caseValue.current_mode !== 'search' && caseValue.lifecycle === 'active'"
        class="privacy-note"
        :data-testid="caseValue.current_mode === 'reconstruction' ? 'web-reconstruction-unavailable' : 'web-search-only-boundary'"
      >
        <strong>{{ locale === 'ru' ? 'В Web доступен физический поиск' : 'Web supports physical search' }}</strong>
        <p v-if="caseValue.current_mode === 'reconstruction'">
          {{ locale === 'ru'
            ? 'Это дело содержит состояние восстановления из plugin/agent workflow. Web сохраняет и показывает эти данные, но не продолжает реконструкцию и не выдаёт AI-предложения в этом режиме.'
            : 'This Case contains reconstruction state from the plugin/agent workflow. Web preserves and displays that evidence, but does not continue reconstruction or request AI proposals in this mode.' }}
        </p>
        <p v-else>
          {{ locale === 'ru'
            ? 'Для этого ранее созданного дела режим ещё не выбран. Web продолжает его только как физический поиск.'
            : 'This earlier Case does not have a selected mode yet. Web continues it only as physical search.' }}
        </p>
        <button class="primary-action" data-testid="switch-to-search" type="button" :disabled="busy" @click="switchToSearch">
          {{ locale === 'ru' ? 'Перейти к физическому поиску' : 'Switch to physical search' }}
        </button>
      </aside>

      <aside v-if="safetyErrorCode" class="system-event" role="alert" data-testid="case-safety-route">
        {{ locale === 'ru'
          ? 'Этот ввод касается потенциально опасного действия. Он не добавлен в дело, и поиск вещей не продолжается автоматически. Не полагайтесь только на воспоминание: проверьте факт надёжным и безопасным способом или обратитесь за подходящей помощью.'
          : 'This input concerns a potentially hazardous action. It was not added to the Case, and lost-item search will not continue automatically. Do not rely on memory alone: verify the fact using a reliable, safe source or seek appropriate help.' }}
        <details><summary>{{ locale === 'ru' ? 'Код маршрута' : 'Route code' }}</summary><code>{{ safetyErrorCode }}</code></details>
        <button class="secondary-action" type="button" :disabled="busy" @click="resumeAfterSafety">
          {{ locale === 'ru' ? 'Вернуться к поиску вещи' : 'Return to lost-item search' }}
        </button>
      </aside>

      <div v-if="errorCode && !executionContractMismatch && !safetyErrorCode" class="privacy-note" role="alert" data-testid="command-error">
        {{ t('case.command_error') }}
        <button
          v-if="retryCommandState"
          class="secondary-action"
          data-testid="retry-command"
          type="button"
          :disabled="busy"
          @click="retryLastCommand"
        >
          {{ locale === 'ru' ? 'Повторить ту же команду' : 'Retry the same command' }}
        </button>
        <details><summary>{{ t('common.details') }}</summary><code>{{ errorCode }}</code></details>
      </div>

      <div v-if="guardCode" class="system-event" data-testid="guard-block">
        {{ t('guard.banner') }}
        <details><summary>{{ t('common.details') }}</summary><code>{{ guardCode }}</code></details>
      </div>

      <aside v-if="executionContractMismatch" class="system-event" role="status" data-testid="execution-contract-mismatch">
        {{ locale === 'ru'
          ? 'Версия приложения и AI-сервиса временно не совпадает. Локальный поиск продолжает работать; восстановите связь и обновите страницу перед следующим AI-предложением.'
          : 'The app and AI service versions are temporarily out of sync. Local search still works; reconnect and refresh before requesting another AI proposal.' }}
      </aside>

      <aside v-if="assistantOfflineFallback" class="system-event" data-testid="assistant-offline-fallback">
        {{ t('assistant.offline_fallback') }}
      </aside>

      <aside v-if="arm === 'assistant' && caseValue.current_mode === 'search'" class="privacy-note" data-testid="provider-disclosure">
        {{ t('privacy.assistant_provider') }}
      </aside>

      <CaseShell
        :case-value="caseValue"
        :proposal="proposal"
        :pending="busy"
        @checked="markChecked"
        @reject="showReject = true"
        @add-search-target="addSearchTarget"
        @journal="scrollJournal"
        @found="showClose = true"
        @pause="pauseCase"
      />

      <EvaluationAbandonAction
        v-if="evaluationSession && evaluationSession.case_id === caseValue.case_id && evaluationSession.outcome === null"
        :evaluation-session-id="evaluationSession.evaluation_session_id"
        :case-id="caseValue.case_id"
      />
      <StorageNotice :engaged="engaged" />
      <InstallEducation :engaged="engaged" />
      <CaseDataActions :case-value="caseValue" />

      <CheckQualityDialog
        v-if="qualityContext"
        :check-id="qualityContext.check_id"
        :target="qualityContext.target"
        :initial-inaccessible-parts="qualityContext.inaccessible_parts"
        :pending="busy"
        @close="suppressedQualityCheckId = qualityContext.check_id"
        @refine="refineQuality"
      />

      <ActionRejectDialog
        v-if="showReject && proposal?.target"
        :target="proposal.target"
        :pending="busy"
        @close="showReject = false"
        @reject="rejectAction"
      />

      <CloseCaseDialog
        v-if="showClose"
        :pending="busy"
        @close="showClose = false"
        @found="closeFound"
        @unresolved="closeUnresolved"
      />
    </template>
  </main>
</template>
