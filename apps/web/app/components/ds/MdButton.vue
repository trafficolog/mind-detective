<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'md' | 'lg' | 'sm'
  icon?: string
  iconRight?: string
  block?: boolean
  disabled?: boolean
  type?: 'button' | 'submit'
}>(), { variant: 'primary', size: 'md', icon: undefined, iconRight: undefined, block: false, disabled: false, type: 'button' })

defineEmits<{ click: [event: MouseEvent] }>()
</script>

<template>
  <button
    :type="type"
    :class="['md-btn', `md-btn--${variant}`, size !== 'md' ? `md-btn--${size}` : '', block ? 'md-btn--block' : '']"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <MdIcon v-if="icon" :name="icon" :size="size === 'lg' ? 22 : 18" :stroke-width="2" />
    <span><slot /></span>
    <MdIcon v-if="iconRight" :name="iconRight" :size="size === 'lg' ? 22 : 18" :stroke-width="2" />
  </button>
</template>
