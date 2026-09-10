<script setup lang="ts">
import { toRaw } from 'vue'
import { caseApiErrorCode, isCaseApiTransportError } from '~/composables/useCaseApi'
import type { ActionFeedbackV2, CaseV2, CommandEnvelope, ProposalModel, SearchMethod } from '~/lib/api/contracts'
import { EXECUTION_CONTRACT_MISMATCH } from '~/lib/api/executionContract'
import { derivePriorCheckAnnotation } from '~/lib/case/derived'
import { appendEvalEvent } from '~/lib/eval/log'

type FoundContext = 'current_suggested_action' | 'elsewhere_unplanned' | 'after_previous_check' | 'unknown'
type RefinedMethod = Exclude<SearchMethod, 'reported_check' | 'inaccessible'>
type RetryableCommand = { caseSnapshot: CaseV2; command: CommandEnvelope }

const route = useRoute()
const repository = useCaseRepository()
const api = useCaseApi()
const arm = useExperimentalArm()
const localExecution = useLocalExecution()
const { locale, t } = useCopy()

const caseValue = ref<CaseV2 | null>(null)
const proposal = ref<ProposalModel | null>(null)
const loading = ref(true)
const busy = ref(false)
const errorCode = ref<string | null>(null)
const guardCode = ref<string | null>(null)
const assistantOfflineFallback = ref(false)
const showComposer = ref(false)
const showReject = ref(false)
const showClose = ref(false)
const suppressedQualityCheckId = ref<string | null>(null)
const retryCommandState = ref<RetryableCommand | null>(null)
const composerText = ref('')

const caseId = computed(() => String(route.params.id || ''))
const executionContractMismatch = computed(() => errorCode.value === EXECUTION_CONTRACT_MISMATCH)
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

function logEvent(event: Parameters<typeof appendEvalEvent>[0], metadata: Record<string, unknown> = {}): void {
  void appendEvalEvent(event, metadata).catch(() => undefined)
}

function snapshotCase(current: CaseV2): CaseV2 {
  return structuredClone(toRaw(current))
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

function setLocalProposal(current: CaseV2): void {
  if (current.current_mode === 'unselected') {
    proposal.value = null
    return
  }
  const next = localExecution.checklistProposal(current, current.current_mode)
  proposal.value = next
  guardCode.value = null
  if (next.kind === 'next_action') {
    logEvent('next_action_shown', {
      case_id: current.case_id,
      arm: arm.value,
      mode: current.current_mode,
      candidate_id: next.candidate_id,
    })
  }
}

function useAssistantFallback(current: CaseV2): void {
  assistantOfflineFallback.value = true
  setLocalProposal(current)
  logEvent('assistant_offline_fallback', {
    case_id: current.case_id,
    arm: arm.value,
    mode: current.current_mode,
  })
}

async function refreshProposal(): Promise<void> {
  const current = caseValue.value
  assistantOfflineFallback.value = false
  if (!current || current.lifecycle !== 'active' || current.current_mode === 'unselected') {
    proposal.value = null
    guardCode.value = null
    return
  }

  if (arm.value === 'checklist') {
    setLocalProposal(current)
    return
  }

  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    useAssistantFallback(current)
    return
  }

  try {
    const response = await api.nextProposal(
      current,
      crypto.randomUUID(),
      new Date().toISOString(),
      current.current_mode,
      locale.value,
      arm.value,
    )
    if (response.case.updated_at !== current.updated_at || response.case.interaction_journal.length !== current.interaction_journal.length) {
      await repository.put(response.case)
      caseValue.value = response.case
    }
    proposal.value = response.proposal
    guardCode.value = response.guard_code
    if (response.proposal.kind === 'next_action') {
      logEvent('next_action_shown', {
        case_id: current.case_id,
        arm: arm.value,
        mode: current.current_mode,
        candidate_id: response.proposal.candidate_id,
      })
    }
    if (response.guard_code) {
      logEvent('ai_guard_blocked', {
        case_id: current.case_id,
        arm: arm.value,
        mode: current.current_mode,
        guard_code: response.guard_code,
      })
    }
  } catch (error: unknown) {
    if ((typeof navigator !== 'undefined' && !navigator.onLine) || isCaseApiTransportError(error)) {
      useAssistantFallback(current)
      return
    }
    const apiCode = caseApiErrorCode(error)
    if (apiCode === EXECUTION_CONTRACT_MISMATCH) {
      errorCode.value = apiCode
      proposal.value = null
      guardCode.value = null
      return
    }
    errorCode.value = 'MD_WEB_PROPOSAL_FAILED'
    proposal.value = null
  }
}

async function runCommand(command: CommandEnvelope, retryCaseSnapshot?: CaseV2): Promise<CaseV2 | null> {
  const current = caseValue.value
  if (!current) return null
  const inputCase = retryCaseSnapshot ? structuredClone(retryCaseSnapshot) : snapshotCase(current)
  busy.value = true
  errorCode.value = null
  try {
    const returned = await localExecution.sendCommand(inputCase, command)
    retryCommandState.value = null
    caseValue.value = returned
    await refreshProposal()
    return returned
  } catch (error: unknown) {
    const code = error instanceof Error ? error.message : 'MD_WEB_LOCAL_EXECUTION_FAILED'
    const normalizedCode = code.startsWith('MD_') ? code : 'MD_WEB_LOCAL_EXECUTION_FAILED'
    errorCode.value = normalizedCode
    if (normalizedCode === 'MD_WEB_LOCAL_EXECUTION_FAILED' || normalizedCode.startsWith('MD_WEB_IDB_')) {
      retryCommandState.value = {
        caseSnapshot: structuredClone(inputCase),
        command: structuredClone(command),
      }
    } else {
      retryCommandState.value = null
    }
    logEvent('local_execution_failed', {
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

async function chooseMode(mode: 'reconstruction' | 'search'): Promise<void> {
  await runCommand(envelope('set_mode', { mode }))
}

async function pauseCase(): Promise<void> {
  const returned = await runCommand(envelope('pause', {}))
  if (returned) logEvent('pause', { case_id: returned.case_id })
}

async function resumeCase(): Promise<void> {
  const returned = await runCommand(envelope('resume', {}))
  if (returned) logEvent('resume', { case_id: returned.case_id })
}

async function markChecked(): Promise<void> {
  const action = proposal.value
  const current = caseValue.value
  if (!action?.target || !current) return
  logEvent('check_started', { case_id: current.case_id, candidate_id: action.candidate_id })
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
    based_on: action.candidate_id ? [action.candidate_id] : [],
    notes: [],
  }))
  if (returned) {
    logEvent('check_finished', { case_id: returned.case_id, candidate_id: action.candidate_id })
  }
}

async function refineQuality(payload: { checkId: string; method: RefinedMethod; inaccessibleParts: string[] }): Promise<void> {
  const returned = await runCommand(envelope('refine_search_check', {
    check_id: payload.checkId,
    method: payload.method,
    inaccessible_parts: payload.inaccessibleParts,
  }))
  if (returned) {
    suppressedQualityCheckId.value = payload.checkId
    logEvent('check_quality_clarified', { case_id: returned.case_id })
  }
}

async function rejectAction(reason: ActionFeedbackV2['reason']): Promise<void> {
  const current = caseValue.value
  const candidateId = proposal.value?.candidate_id
  if (!current || !candidateId) return
  const returned = await runCommand(envelope('reject_next_action', {
    feedback_id: crypto.randomUUID(),
    candidate_id: candidateId,
    reason,
  }))
  if (returned) {
    showReject.value = false
    logEvent('next_action_rejected', { case_id: returned.case_id, candidate_id: candidateId, reason_code: reason })
  }
}

async function closeFound(context: FoundContext): Promise<void> {
  const returned = await runCommand(envelope('close_found', { outcome: { found_context: context } }))
  if (returned) {
    showClose.value = false
    proposal.value = null
    logEvent('found', { case_id: returned.case_id })
    logEvent('found_context_recorded', { case_id: returned.case_id, found_context: context })
  }
}

async function closeUnresolved(): Promise<void> {
  const returned = await runCommand(envelope('close_unresolved', { outcome: {} }))
  if (returned) {
    showClose.value = false
    proposal.value = null
    logEvent('case_closed_unresolved', { case_id: returned.case_id })
  }
}

async function submitComposer(): Promise<void> {
  const text = composerText.value.trim()
  const current = caseValue.value
  if (!text || !current) return
  const returned = await runCommand(envelope('add_statement', {
    statement_id: crypto.randomUUID(),
    source: 'user',
    statement_type: current.current_mode === 'search' ? 'search_suggestion' : 'recollection',
    original_text: text,
    event_time: null,
    user_confirmation: true,
    supporting_evidence_ids: [],
    limitations: [],
  }))
  if (returned) {
    composerText.value = ''
    showComposer.value = false
  }
}

function handleDeleted(): void {
  caseValue.value = null
  proposal.value = null
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
      <CaseDataActions :case-value="caseValue" :allow-delete="true" @deleted="handleDeleted" />
    </template>

    <template v-else>
      <div v-if="caseValue.lifecycle === 'paused'" class="privacy-note" data-testid="paused-banner">
        {{ t('case.paused_copy') }}
        <button class="primary-action" type="button" :disabled="busy" @click="resumeCase">{{ t('case.resume') }}</button>
      </div>

      <div v-if="caseValue.current_mode === 'unselected' && caseValue.lifecycle === 'active'" class="privacy-note" data-testid="mode-choice">
        <strong>{{ t('case.mode_question') }}</strong>
        <p>{{ t('case.mode_help') }}</p>
        <div class="dialog-actions">
          <button class="secondary-action" type="button" :disabled="busy" @click="chooseMode('reconstruction')">{{ t('case.mode_reconstruct_action') }}</button>
          <button class="primary-action" type="button" :disabled="busy" @click="chooseMode('search')">{{ t('case.mode_search_action') }}</button>
        </div>
      </div>

      <div v-if="errorCode && !executionContractMismatch" class="privacy-note" role="alert" data-testid="command-error">
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

      <aside v-if="arm === 'assistant'" class="privacy-note" data-testid="provider-disclosure">
        {{ t('privacy.assistant_provider') }}
      </aside>

      <CaseShell
        :case-value="caseValue"
        :proposal="proposal"
        :pending="busy"
        @checked="markChecked"
        @reject="showReject = true"
        @write="showComposer = true"
        @journal="scrollJournal"
        @found="showClose = true"
        @pause="pauseCase"
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

      <div v-if="showComposer" class="dialog-backdrop" data-testid="composer-dialog" @click.self="showComposer = false">
        <section class="dialog-sheet" role="dialog" aria-modal="true" aria-labelledby="composer-title">
          <h2 id="composer-title">{{ t('composer.title') }}</h2>
          <form @submit.prevent="submitComposer">
            <label class="field-label" for="composer-text">
              {{ caseValue.current_mode === 'search' ? t('composer.search_label') : t('composer.label') }}
            </label>
            <textarea id="composer-text" v-model="composerText" rows="4" required />
            <div class="dialog-actions">
              <button class="secondary-action" type="button" @click="showComposer = false">{{ t('common.cancel') }}</button>
              <button class="primary-action" type="submit" :disabled="busy || !composerText.trim()">{{ t('common.save') }}</button>
            </div>
          </form>
        </section>
      </div>
    </template>
  </main>
</template>