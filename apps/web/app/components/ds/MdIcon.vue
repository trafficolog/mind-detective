<script setup lang="ts">
import { computed } from 'vue'
import { ICONS } from '~/lib/ds/icons'

const props = withDefaults(defineProps<{
  name: string
  size?: number
  strokeWidth?: number
  color?: string
  label?: string
}>(), { size: 20, strokeWidth: 1.9, color: undefined, label: undefined })

const inner = computed(() => ICONS[props.name] ?? '')
</script>

<template>
  <span
    class="md-icon"
    :role="label ? 'img' : undefined"
    :aria-label="label"
    :aria-hidden="label ? undefined : 'true'"
    :data-icon="name"
    :style="{ display: 'inline-flex', width: `${size}px`, height: `${size}px`, flex: 'none', color, lineHeight: 0 }"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      :width="size"
      :height="size"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      stroke-linecap="round"
      stroke-linejoin="round"
      v-html="inner"
    />
  </span>
</template>
