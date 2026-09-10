<script setup lang="ts">
import type { ActionFeedbackV2, CaseV2, CommandEnvelope, ProposalModel, SearchMethod } from '~/lib/api/contracts'
import { derivePriorCheckAnnotation } from '~/lib/case/derived'
import { appendEvalEvent } from '~/lib/eval/log'

type FoundContext = 'current_suggested_action' | 'elsewhere_unplanned' | 'after_previous_check' | 'unknown'
type RefinedMethod = Exclude<SearchMethod, 'reported_check' | 'inaccessible'>

const route = useRoute()
const repository = useCaseRepository()
const api = useCaseApi()
const arm = useExperimentalArm()
const queue = useCommandQueue()

const caseValue = ref<CaseV2 | null>(null)
const proposal = ref<ProposalModel | null>(null)
const loading = ref(true)
const busy = ref(false)
const errorCode = ref<string | null>(null)
const guardCode = ref<string | null>(null)
const showComposer = ref(false)
const showReject = ref(false)
const showClose = ref(false)
const suppressedQualityCheckId = ref<string | null>(null)
const composerText = ref('')

const caseId = computed(() => String(route.params.id || ''))
const failedCommand = computed(() => [...queue.commands.value].reverse().find(command => command.status === 'failed') ?? null)
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

function logEvent(event: Parameters<typeof appendEvalEvent>[0], metadata: Record<string, unknown> = {}): void {
  void appendEvalEvent(event, metadata).catch(() => undefined)
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

async function refreshProposal(): Promise<void> {
  const current = caseValue.value
  if (!current || current.lifecycle !== 'active' || current.current_mode === 'unselected') {
    proposal.value = null
    guardCode.value = null
    return
  }
  try {
    const response = await api.nextProposal(
      current,
      crypto.randomUUID(),
      new Date().toISOString(),
      current.current_mode,
      'ru',
      arm.value,
    )
    if (response.case.updated_at !== current.updated_at || response.case.interaction_journal.length !== current.interaction_journal.length) {
      await repository.put(response.case)
      caseValue.value = response.case
    }
    proposal.value = response.proposal
    guardCode.value = response.guard_code
    if (response.proposal.kind === 'next_action') {
      logEvent('next_action_shown', { case_id: current.case_id, arm: arm.value, mode: current.current_mode, candidate_id: response.proposal.candidate_id })
    }
    if (response.guard_code) {
      logEvent('ai_guard_blocked', { case_id: current.case_id, arm: arm.value, mode: current.current_mode, guard_code: response.guard_code })
    }
  } catch {
    errorCode.value = 'MD_WEB_PROPOSAL_FAILED'
    proposal.value = null
  }
}

async function runCommand(command: CommandEnvelope): Promise<CaseV2 | null> {
  if (!caseValue.value) return null
  busy.value = true
  errorCode.value = null
  logEvent('pending_command_started', { case_id: caseValue.value.case_id, command_id: command.command_id })
  try {
    const returned = await queue.enqueue(caseValue.value, command)
    caseValue.value = returned
    await refreshProposal()
    return returned
  } catch {
    errorCode.value = failedCommand.value?.error_code ?? 'MD_WEB_COMMAND_FAILED'
    logEvent('pending_command_failed', { case_id: caseValue.value.case_id, command_id: command.command_id, outcome_code: errorCode.value })
    return null
  } finally {
    busy.value = false
  }
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
    suppressedQualityCheckId.value = checkId
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
    statement_type: current.current_mode === 'search' ? 'observation' : 'recollection',
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

async function retryFailed(): Promise<void> {
  const failed = failedCommand.value
  if (!failed) return
  busy.value = true
  errorCode.value = null
  logEvent('pending_command_retried', { case_id: failed.case_id, command_id: failed.command_id })
  try {
    const returned = await queue.retry(failed.command_id)
    caseValue.value = returned
    await refreshProposal()
  } catch {
    errorCode.value = failed.error_code ?? 'MD_WEB_COMMAND_FAILED'
  } finally {
    busy.value = false
  }
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
    <p v-if="loading" class="muted" aria-live="polite">Загружаем дело…</p>
    <section v-else-if="!caseValue" class="hero-panel">
      <h1>Дело не найдено</h1>
      <p class="lede">Оно могло быть удалено из локального хранилища этого браузера.</p>
      <NuxtLink class="primary-action" to="/">К списку дел</NuxtLink>
    </section>

    <CaseOutcome v-else-if="caseValue.lifecycle === 'closed_found' || caseValue.lifecycle === 'closed_unresolved'" :case-value="caseValue" />

    <template v-else>
      <div v-if="caseValue.lifecycle === 'paused'" class="privacy-note" data-testid="paused-banner">
        Поиск приостановлен. История сохранена без изменений.
        <button class="primary-action" type="button" :disabled="busy" @click="resumeCase">Продолжить</button>
      </div>

      <div v-if="caseValue.current_mode === 'unselected' && caseValue.lifecycle === 'active'" class="privacy-note" data-testid="mode-choice">
        <strong>С чего полезнее продолжить?</strong>
        <p>Можно сначала восстановить подтверждённую последовательность или перейти к физическому поиску.</p>
        <div class="dialog-actions">
          <button class="secondary-action" type="button" :disabled="busy" @click="chooseMode('reconstruction')">Восстановить последовательность</button>
          <button class="primary-action" type="button" :disabled="busy" @click="chooseMode('search')">Перейти к поиску</button>
        </div>
      </div>

      <div v-if="errorCode" class="privacy-note" role="alert" data-testid="command-error">
        Изменение не сохранено. Каноническое состояние дела не менялось.
        <button v-if="failedCommand" class="secondary-action" type="button" :disabled="busy" @click="retryFailed">Повторить ту же команду</button>
      </div>

      <div v-if="guardCode" class="system-event" data-testid="guard-block">
        Предложение помощника не прошло проверку безопасности. Показан безопасный резервный шаг.
        <details><summary>Техническая причина</summary><code>{{ guardCode }}</code></details>
      </div>

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
          <h2 id="composer-title">Добавить подтверждённую информацию</h2>
          <form @submit.prevent="submitComposer">
            <label class="field-label" for="composer-text">Что вы помните или наблюдаете?</label>
            <textarea id="composer-text" v-model="composerText" rows="4" required />
            <div class="dialog-actions">
              <button class="secondary-action" type="button" @click="showComposer = false">Отмена</button>
              <button class="primary-action" type="submit" :disabled="busy || !composerText.trim()">Сохранить</button>
            </div>
          </form>
        </section>
      </div>
    </template>
  </main>
</template>
