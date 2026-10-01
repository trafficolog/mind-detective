<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  done?: number
  total?: number
  unit?: string
  label?: string
  variant?: 'bar' | 'segments'
  mode?: 'search' | 'reconstruction'
}>(), { done: 0, total: 0, unit: 'проверок', label: undefined, variant: 'bar', mode: 'search' })

const pct = computed(() => (props.total > 0 ? Math.min(100, (props.done / props.total) * 100) : 0))
const fill = computed(() => props.mode === 'reconstruction'
  ? 'linear-gradient(90deg,var(--brand-400),var(--brand-600))'
  : 'linear-gradient(90deg,#3BB6C8,var(--mode-search-accent))')
const aria = computed(() => `${props.done} из ${props.total} ${props.unit}`)
</script>

<template>
  <div style="display:grid;gap:8px">
    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px">
      <span v-if="label" style="font-size:15px;line-height:20px;font-weight:600;color:var(--text-primary)">{{ label }}</span>
      <span v-else />
      <span style="font-size:15px;line-height:20px;color:var(--text-secondary);font-variant-numeric:tabular-nums"><b style="color:var(--text-primary);font-weight:700">{{ done }}</b> из {{ total }} {{ unit }}</span>
    </div>
    <div v-if="variant === 'segments'" role="img" :aria-label="aria" :style="{ display: 'grid', gridTemplateColumns: `repeat(${Math.max(total, 1)},1fr)`, gap: '4px' }">
      <span v-for="i in total" :key="i" :style="{ height: '8px', borderRadius: '4px', background: i - 1 < done ? fill : 'rgba(164,201,236,.35)' }" />
    </div>
    <div v-else role="progressbar" :aria-valuemin="0" :aria-valuemax="total" :aria-valuenow="done" :aria-label="aria" style="height:10px;border-radius:5px;background:rgba(164,201,236,.35);overflow:hidden">
      <div :style="{ width: `${pct}%`, height: '100%', borderRadius: '5px', background: fill, transition: 'width var(--dur-slow) var(--ease-standard)' }" />
    </div>
  </div>
</template>
