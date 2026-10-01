<script setup lang="ts">
withDefaults(defineProps<{
  icon: string
  label: string
  variant?: 'glass' | 'plain' | 'filled'
  size?: number
}>(), { variant: 'glass', size: 44 })

defineEmits<{ click: [event: MouseEvent] }>()
</script>

<template>
  <button
    type="button"
    :aria-label="label"
    :title="label"
    :class="['md-iconbtn', `md-iconbtn--${variant}`]"
    :style="{ width: `${size}px`, height: `${size}px` }"
    @click="$emit('click', $event)"
  >
    <MdIcon :name="icon" :size="Math.round(size * 0.46)" :stroke-width="2" />
  </button>
</template>
