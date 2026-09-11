<script setup lang="ts">
import type { EvaluationSessionV1 } from '~/lib/eval/contracts'

const emit = defineEmits<{
  started: [session: EvaluationSessionV1]
}>()

const evaluation = useEvaluationSession()
const enrollmentSlot = ref('1')
const pending = ref(false)
const errorCode = ref<string | null>(null)

async function startStaged(): Promise<void> {
  const slot = Number(enrollmentSlot.value)
  pending.value = true
  errorCode.value = null
  try {
    emit('started', await evaluation.startStagedSession(slot))
  } catch (error: unknown) {
    errorCode.value = error instanceof Error ? error.message : 'MD_WEB_EVAL_START_FAILED'
  } finally {
    pending.value = false
  }
}

async function startReal(): Promise<void> {
  pending.value = true
  errorCode.value = null
  try {
    emit('started', await evaluation.startRealSession())
  } catch (error: unknown) {
    errorCode.value = error instanceof Error ? error.message : 'MD_WEB_EVAL_START_FAILED'
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <section class="privacy-note" data-testid="evaluation-start-panel">
    <h2>Evaluation session</h2>
    <p>Assignment создаётся до Case и после этого не меняется.</p>

    <form @submit.prevent="startStaged">
      <label class="field-label" for="evaluation-enrollment-slot">Staged enrollment slot</label>
      <input
        id="evaluation-enrollment-slot"
        v-model="enrollmentSlot"
        data-testid="evaluation-enrollment-slot"
        type="number"
        min="1"
        step="1"
        :disabled="pending"
        required
      >
      <button class="primary-action" data-testid="start-staged-evaluation" type="submit" :disabled="pending">
        Начать staged session
      </button>
    </form>

    <button class="secondary-action" data-testid="start-real-evaluation" type="button" :disabled="pending" @click="startReal">
      Начать real-pilot session
    </button>

    <p v-if="errorCode" class="error-copy" role="alert" data-testid="evaluation-start-error">{{ errorCode }}</p>
  </section>
</template>
