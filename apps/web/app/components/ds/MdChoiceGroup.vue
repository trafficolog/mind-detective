<script setup lang="ts">
defineProps<{
  label?: string
  options: Array<{ value: string, label: string, icon?: string }>
  modelValue?: string
  columns?: number
}>()
defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <div role="radiogroup" :aria-label="label" style="display:grid;gap:8px">
    <span v-if="label" class="md-field__label">{{ label }}</span>
    <div class="md-choices" :style="{ gridTemplateColumns: `repeat(${columns ?? 2},minmax(0,1fr))` }">
      <button
        v-for="o in options"
        :key="o.value"
        type="button"
        role="radio"
        :aria-checked="modelValue === o.value"
        class="md-choice"
        @click="$emit('update:modelValue', o.value)"
      >
        <span v-if="o.icon" class="md-choice__icon"><MdIcon :name="o.icon" :size="20" /></span>
        <span style="flex:1;min-width:0">{{ o.label }}</span>
        <MdIcon v-if="modelValue === o.value" name="check" :size="18" :stroke-width="2.4" color="var(--brand-600)" />
      </button>
    </div>
  </div>
</template>
