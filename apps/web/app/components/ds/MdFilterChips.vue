<script setup lang="ts">
withDefaults(defineProps<{
  options: Array<{ value: string, label: string, count?: number }>
  modelValue?: string
  label?: string
}>(), { modelValue: undefined, label: 'Фильтр' })
defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <div class="md-filters" role="toolbar" :aria-label="label">
    <button
      v-for="o in options"
      :key="o.value"
      type="button"
      class="md-filter"
      :aria-pressed="modelValue === o.value"
      @click="$emit('update:modelValue', o.value)"
    >
      <span>{{ o.label }}</span>
      <span v-if="o.count !== undefined" class="md-filter__count">{{ o.count }}</span>
    </button>
  </div>
</template>
