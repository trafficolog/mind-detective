<script setup lang="ts">
import type { ExperimentalArm, InteractionMode } from '~/lib/api/contracts'

const props = defineProps<{
  mode: InteractionMode
  arm: ExperimentalArm
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
    <span aria-hidden="true">·</span>
    <span data-testid="experimental-arm">{{ arm === 'assistant' ? 'AI-предложение' : 'Контрольный список' }}</span>
  </div>
</template>
