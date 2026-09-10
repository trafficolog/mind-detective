<script setup lang="ts">
import type { InteractionMode } from '~/lib/api/contracts'

const props = defineProps<{
  mode: InteractionMode
}>()

const label = computed(() => {
  if (props.mode === 'reconstruction') return 'Восстановление последовательности'
  if (props.mode === 'search') return 'Физический поиск'
  return 'Режим не выбран'
})
</script>

<template>
  <div class="mode-banner" data-testid="mode-banner">
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
      <path d="M12 3a9 9 0 1 0 9 9" />
      <path d="M12 7v5l3 2" />
    </svg>
    <strong>{{ label }}</strong>
  </div>
</template>
