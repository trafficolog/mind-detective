<script setup lang="ts">
import type { JournalEntryV2 } from '~/lib/api/contracts'

const props = defineProps<{ entry: JournalEntryV2 }>()

const isGuardEvent = computed(() => props.entry.text === 'guard.ai_proposal_blocked')
const reviewedCopy = computed(() => {
  if (isGuardEvent.value) {
    return 'Предложение помощника не прошло проверку безопасности. Для продолжения используется безопасный резервный шаг.'
  }
  return props.entry.text
})
</script>

<template>
  <aside class="system-event" :data-testid="`journal-entry-${entry.id}`">
    <strong>{{ isGuardEvent ? 'Безопасность' : 'Системное событие' }}</strong>
    <div>{{ reviewedCopy }}</div>
  </aside>
</template>
