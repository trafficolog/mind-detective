<script setup lang="ts">
import { computed, useAttrs } from 'vue'

const props = withDefaults(defineProps<{
  variant?: 'default' | 'interactive' | 'selected' | 'confirmed' | 'unknown' | 'contradiction' | 'research' | 'disabled'
  tone?: 'primary' | 'secondary'
  padding?: number | string
  radius?: number
  as?: string
}>(), { variant: 'default', tone: 'primary', padding: 16, radius: undefined, as: undefined })

const attrs = useAttrs()
const interactive = computed(() => props.variant === 'interactive' || Boolean(attrs.onClick))
const tag = computed(() => props.as ?? (interactive.value ? 'button' : 'div'))
const cls = computed(() => [
  'md-glass',
  props.tone === 'secondary' ? 'md-glass--secondary' : '',
  interactive.value ? 'md-glass--interactive' : '',
  props.variant !== 'default' && props.variant !== 'interactive' ? `md-glass--${props.variant}` : '',
])
const style = computed(() => ({
  padding: typeof props.padding === 'number' ? `${props.padding}px` : props.padding,
  borderRadius: props.radius !== undefined ? `${props.radius}px` : undefined,
}))
</script>

<template>
  <component
    :is="tag"
    :class="cls"
    :type="tag === 'button' ? 'button' : undefined"
    :aria-disabled="variant === 'disabled' || undefined"
    :style="style"
  >
    <slot />
  </component>
</template>
