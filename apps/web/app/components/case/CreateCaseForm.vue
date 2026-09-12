<script setup lang="ts">
import type { CaseV2, CommandEnvelope } from '~/lib/api/contracts'
import { startEvaluationSessionCase } from '~/lib/eval/store'
import { safetyCodeForInput } from '~/lib/safety'

const props = withDefaults(defineProps<{
  evaluationSessionId?: string | null
}>(), {
  evaluationSessionId: null,
})

const emit = defineEmits<{
  created: [caseValue: CaseV2]
}>()

const localExecution = useLocalExecution()
const { locale } = useCopy()
const itemLabel = ref('')
const pending = ref(false)
const errorCode = ref<string | null>(null)
const safetyError = computed(() => errorCode.value?.startsWith('MD_SAFE_') ? errorCode.value : null)

function executionErrorCode(error: unknown, fallback: string): string {
  if (error && typeof error === 'object' && 'code' in error && typeof error.code === 'string') {
    return error.code
  }
  return error instanceof Error ? error.message : fallback
}

async function submit(): Promise<void> {
  const label = itemLabel.value.trim()
  if (!label || pending.value) return
  errorCode.value = null
  const safetyCode = safetyCodeForInput(label)
  if (safetyCode) {
    errorCode.value = safetyCode
    return
  }

  pending.value = true
  const caseId = crypto.randomUUID()
  const now = new Date().toISOString()
  try {
    const created = await localExecution.createCase(caseId, label, now)
    const selectSearch: CommandEnvelope = {
      command_id: crypto.randomUUID(),
      expected_updated_at: created.updated_at,
      command_type: 'set_mode',
      now,
      payload: { mode: 'search' },
    }
    const caseValue = await localExecution.sendCommand(created, selectSearch)
    if (props.evaluationSessionId) {
      await startEvaluationSessionCase(props.evaluationSessionId, caseValue.case_id, now)
    }
    emit('created', caseValue)
    itemLabel.value = ''
  } catch (error: unknown) {
    const code = executionErrorCode(error, 'create.failed')
    errorCode.value = code.startsWith('MD_WEB_EVAL_') ? code : 'create.failed'
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <form class="create-case" data-testid="create-case-form" @submit.prevent="submit">
    <label class="field-label" for="item-label">Что потерялось?</label>
    <input
      id="item-label"
      v-model="itemLabel"
      data-testid="item-label"
      name="item-label"
      type="text"
      autocomplete="off"
      enterkeyhint="go"
      placeholder="Например, ключи"
      :disabled="pending"
      required
    >
    <button class="primary-action" data-testid="start-search" type="submit" :disabled="pending || !itemLabel.trim()" :aria-busy="pending">
      {{ pending ? 'Создаём дело…' : 'Начать поиск' }}
    </button>
    <aside v-if="safetyError" class="system-event" role="alert" data-testid="safety-route">
      {{ locale === 'ru'
        ? 'Этот запрос касается потенциально опасного действия, поэтому MIND Detective не использует поиск вещей для ответа. Не полагайтесь только на воспоминание: проверьте факт надёжным и безопасным способом или обратитесь за подходящей помощью.'
        : 'This request concerns a potentially hazardous action, so MIND Detective does not use lost-item search to answer it. Do not rely on memory alone: verify the fact using a reliable, safe source or seek appropriate help.' }}
      <details><summary>{{ locale === 'ru' ? 'Код маршрута' : 'Route code' }}</summary><code>{{ safetyError }}</code></details>
    </aside>
    <p v-else-if="errorCode" class="error-copy" role="alert">
      {{ errorCode.startsWith('MD_WEB_EVAL_') ? 'Не удалось привязать дело к evaluation-сессии. Данные эксперимента не записаны.' : 'Не удалось создать дело. Попробуйте ещё раз.' }}
    </p>
  </form>
</template>
