<script setup lang="ts">
import { finishEvaluationSession } from '~/lib/eval/store'

const props = defineProps<{
  evaluationSessionId: string
  caseId: string
}>()

const evaluation = useEvaluationSession()
const pending = ref(false)
const errorCode = ref<string | null>(null)

async function abandon(): Promise<void> {
  if (pending.value) return
  pending.value = true
  errorCode.value = null
  try {
    evaluation.session.value = await finishEvaluationSession(
      props.evaluationSessionId,
      'abandoned',
      new Date().toISOString(),
      { case_id: props.caseId },
    )
    await navigateTo('/evaluation')
  } catch (error: unknown) {
    errorCode.value = error instanceof Error ? error.message : 'MD_WEB_EVAL_ABANDON_FAILED'
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <section class="privacy-note">
    <strong>Evaluation session</strong>
    <p>Можно завершить участие в оценке, не закрывая и не изменяя сам Case.</p>
    <button
      class="secondary-action"
      data-testid="evaluation-abandon"
      type="button"
      :disabled="pending"
      @click="abandon"
    >
      Завершить участие в evaluation
    </button>
    <p v-if="errorCode" role="alert"><code>{{ errorCode }}</code></p>
  </section>
</template>
