<script setup lang="ts">
import { useId } from 'vue'

const props = withDefaults(defineProps<{
  label?: string
  modelValue?: string
  placeholder?: string
  maxLength?: number
  rows?: number
  hint?: string
  id?: string
  readonly?: boolean
}>(), { label: undefined, modelValue: '', placeholder: undefined, maxLength: undefined, rows: 5, hint: undefined, id: undefined, readonly: false })

defineEmits<{ 'update:modelValue': [value: string] }>()
const fid = props.id ?? `md-ta-${useId()}`
</script>

<template>
  <div class="md-field">
    <label v-if="label" class="md-field__label" :for="fid">{{ label }}</label>
    <textarea
      :id="fid"
      class="md-textarea"
      :rows="rows"
      :placeholder="placeholder"
      :maxlength="maxLength"
      :value="modelValue"
      :readonly="readonly"
      :aria-label="label ? undefined : placeholder"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
    <div v-if="hint || maxLength" class="md-field__foot">
      <span>{{ hint }}</span>
      <span v-if="maxLength" style="font-variant-numeric:tabular-nums">{{ modelValue.length }} / {{ maxLength }}</span>
    </div>
  </div>
</template>
