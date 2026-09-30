<script setup lang="ts">
import { computed } from 'vue'

const TONE: Record<string, [string, string, string]> = {
  unknown: ['md-glass--unknown', 'var(--unknown-fg)', 'circle-help'],
  contradiction: ['md-glass--contradiction', 'var(--contradiction-fg)', 'triangle-alert'],
  confirmed: ['md-glass--confirmed', 'var(--confirmed-fg)', 'circle-check'],
  research: ['md-glass--research', 'var(--research-fg)', 'flask-conical'],
  hypothesis: ['', 'var(--hypothesis-fg)', 'lightbulb'],
  neutral: ['', 'var(--brand-600)', 'info'],
}
const props = withDefaults(defineProps<{
  tone?: string
  icon?: string
  title: string
  count?: number
}>(), { tone: 'neutral', icon: undefined, count: undefined })
const t = computed(() => TONE[props.tone] ?? TONE.neutral!)
</script>

<template>
  <div :class="'md-glass ' + t[0]" :data-tone="tone" style="display:flex;gap:14px;padding:16px 16px;border-radius:22px;align-items:flex-start">
    <MdIcon :name="icon ?? t[2]" :size="28" :color="t[1]" :stroke-width="2" style="margin-top:1px" />
    <span style="flex:1;min-width:0;display:grid;gap:6px">
      <span style="display:flex;align-items:center;gap:10px">
        <span style="flex:1;font-size:18px;line-height:24px;font-weight:650;color:var(--text-primary)">{{ title }}</span>
        <span v-if="count !== undefined" data-testid="state-count" style="font-size:20px;line-height:24px;font-weight:700;color:var(--text-primary);font-variant-numeric:tabular-nums">{{ count }}</span>
      </span>
      <span v-if="$slots.default" style="font-size:15px;line-height:21px;color:var(--text-secondary)"><slot /></span>
    </span>
  </div>
</template>
