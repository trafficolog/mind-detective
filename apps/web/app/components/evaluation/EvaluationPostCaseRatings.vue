<script setup lang="ts">
import { appendEvalEvent } from '~/lib/eval/log'

const props = defineProps<{
  evaluationSessionId: string
}>()

const taskLoad = ref('')
const convenience = ref('')
const pending = ref(false)
const saved = ref(false)
const errorCode = ref<string | null>(null)

async function save(): Promise<void> {
  if (pending.value || saved.value) return
  const task = Number(taskLoad.value)
  const ease = Number(convenience.value)
  if (!Number.isInteger(task) || task < 1 || task > 5 || !Number.isInteger(ease) || ease < 1 || ease > 5) {
    errorCode.value = 'MD_WEB_EVAL_RATING'
    return
  }
  pending.value = true
  errorCode.value = null
  try {
    await appendEvalEvent(props.evaluationSessionId, 'post_case_rating', {
      task_load: task,
      convenience: ease,
    })
    saved.value = true
  } catch (error: unknown) {
    errorCode.value = error instanceof Error ? error.message : 'MD_WEB_EVAL_RATING_SAVE'
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <section class="privacy-note" data-testid="evaluation-ratings">
    <strong>Оценка после поиска</strong>
    <p>Только фиксированные оценки 1–5. Текстовые комментарии здесь не собираются.</p>
    <template v-if="!saved">
      <label class="field-label" for="evaluation-task-load">Нагрузка</label>
      <select id="evaluation-task-load" v-model="taskLoad" data-testid="evaluation-task-load" :disabled="pending">
        <option value="" disabled>Выберите 1–5</option>
        <option v-for="value in 5" :key="`load-${value}`" :value="String(value)">{{ value }}</option>
      </select>
      <label class="field-label" for="evaluation-convenience">Удобство</label>
      <select id="evaluation-convenience" v-model="convenience" data-testid="evaluation-convenience" :disabled="pending">
        <option value="" disabled>Выберите 1–5</option>
        <option v-for="value in 5" :key="`convenience-${value}`" :value="String(value)">{{ value }}</option>
      </select>
      <button
        class="primary-action"
        data-testid="save-evaluation-ratings"
        type="button"
        :disabled="pending || !taskLoad || !convenience"
        @click="save"
      >
        Сохранить оценки
      </button>
      <p v-if="errorCode" role="alert"><code>{{ errorCode }}</code></p>
    </template>
    <p v-else data-testid="evaluation-ratings-saved">Оценки сохранены локально.</p>
  </section>
</template>
