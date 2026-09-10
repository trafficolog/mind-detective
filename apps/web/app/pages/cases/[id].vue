<script setup lang="ts">
import type { CaseV2, CommandEnvelope, ProposalModel } from '~/lib/api/contracts'

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
const composerText = ref('')

const caseId = computed(() => String(route.params.id || ''))
const failedCommand = computed(() => [...queue.commands.value].reverse().find(command => command.status === 'failed') ?? null)

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
    return
  }
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
}

async function runCommand(command: CommandEnvelope): Promise<CaseV2> {
  if (!caseValue.value) throw new Error('MD_WEB_CASE_NOT_LOADED')
  busy.value = true
  errorCode.value = null
  try {
    const returned = await queue.enqueue(caseValue.value, command)
    caseValue.value = returned
    await refreshProposal()
    return returned
  } catch (error: unknown) {
    errorCode.value = failedCommand.value?.error_code ?? 'MD_WEB_COMMAND_FAILED'
    throw error
  } finally {
    busy.value = false
  }
}

async function chooseMode(mode: 'reconstruction' | 'search'): Promise<void> {
  await runCommand(envelope('set_mode', { mode }))
}

async function resumeCase(): Promise<void> {
  await runCommand(envelope('resume', {}))
}

async function markChecked(): Promise<void> {
  const action = proposal.value
  if (!action?.target) return
  await runCommand(envelope('record_search_check', {
    check_id: crypto.randomUUID(),
    target: action.target,
    method: 'reported_check',
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    result: 'not_found',
    inaccessible_parts: [],
    based_on: action.candidate_id ? [action.candidate_id] : [],
    notes: [],
  }))
}

async function submitComposer(): Promise<void> {
  const text = composerText.value.trim()
  const current = caseValue.value
  if (!text || !current) return
  await runCommand(envelope('add_statement', {
    statement_id: crypto.randomUUID(),
    source: 'user',
    statement_type: current.current_mode === 'search' ? 'observation' : 'recollection',
    original_text: text,
    event_time: null,
    user_confirmation: true,
    supporting_evidence_ids: [],
    limitations: [],
  }))
  composerText.value = ''
  showComposer.value = false
}

async function retryFailed(): Promise<void> {
  const failed = failedCommand.value
  if (!failed) return
  busy.value = true
  errorCode.value = null
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
        :arm="arm"
        :proposal="proposal"
        :pending="busy"
        @checked="markChecked"
        @write="showComposer = true"
        @journal="scrollJournal"
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
