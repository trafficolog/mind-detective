<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'

const emit = defineEmits<{
  created: [caseValue: CaseV2]
}>()

const localExecution = useLocalExecution()
const itemLabel = ref('')
const pending = ref(false)
const errorCode = ref<string | null>(null)

async function submit(): Promise<void> {
  const label = itemLabel.value.trim()
  if (!label || pending.value) return
  pending.value = true
  errorCode.value = null
  const caseId = crypto.randomUUID()
  const now = new Date().toISOString()
  try {
    const caseValue = await localExecution.createCase(caseId, label, now)
    emit('created', caseValue)
    itemLabel.value = ''
  } catch {
    errorCode.value = 'create.failed'
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
    <p v-if="errorCode" class="error-copy" role="alert">Не удалось создать дело. Попробуйте ещё раз.</p>
  </form>
</template>