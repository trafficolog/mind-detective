<script setup lang="ts">
import type { JournalEntryV2 } from '~/lib/api/contracts'

const props = defineProps<{ entries: readonly JournalEntryV2[] }>()

function modeLabel(mode: JournalEntryV2['mode']): string {
  if (mode === 'reconstruction') return 'Восстановление'
  if (mode === 'search') return 'Поиск'
  return 'Система'
}
</script>

<template>
  <section class="interaction-journal" aria-labelledby="journal-title" data-testid="interaction-journal">
    <h2 id="journal-title">Журнал</h2>
    <p v-if="!props.entries.length" class="muted">Здесь появятся подтверждённые шаги и системные события.</p>
    <article v-for="entry in props.entries" :key="entry.id" class="journal-entry" :data-testid="`journal-entry-${entry.id}`">
      <div class="journal-entry__meta">
        <span>{{ modeLabel(entry.mode) }}</span>
        <span>{{ entry.author === 'user' ? 'Вы' : entry.author === 'assistant' ? 'Помощник' : 'Система' }}</span>
      </div>
      <div>{{ entry.text }}</div>
    </article>
  </section>
</template>
