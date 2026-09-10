<script setup lang="ts">
import type { JournalEntryV2 } from '~/lib/api/contracts'

const props = defineProps<{ entry: JournalEntryV2 }>()

const reviewedCopy = computed(() => {
  if (props.entry.text === 'guard.ai_proposal_blocked') {
    return 'Предложение помощника не прошло проверку. Для продолжения используется безопасный резервный шаг.'
  }
  return props.entry.text
})
</script>

<template>
  <aside class="system-event" :data-testid="`system-event-${entry.id}`">
    <strong>Системное событие</strong>
    <div>{{ reviewedCopy }}</div>
  </aside>
</template>
