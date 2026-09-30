<script setup lang="ts">
import { computed } from 'vue'

const TONE: Record<string, [string, string, string, string]> = {
  privacy: ['md-glass--confirmed', 'shield-check', 'var(--confirmed-fg)', 'rgba(5,135,91,.12)'],
  offline: ['', 'wifi-off', 'var(--neutral-ink)', 'var(--neutral-bg)'],
  research: ['md-glass--research', 'flask-conical', 'var(--research-fg)', 'rgba(122,53,216,.12)'],
  warning: ['md-glass--unknown', 'circle-alert', 'var(--unknown-fg)', 'rgba(184,120,0,.12)'],
  error: ['md-glass--contradiction', 'file-warning', 'var(--contradiction-fg)', 'rgba(217,56,69,.1)'],
  info: ['', 'info', 'var(--brand-600)', 'var(--brand-50)'],
}
const props = withDefaults(defineProps<{ tone?: string, icon?: string, title?: string, compact?: boolean }>(), { tone: 'info', icon: undefined, title: undefined, compact: false })
const t = computed(() => TONE[props.tone] ?? TONE.info!)
</script>

<template>
  <aside
    :class="'md-glass ' + t[0]"
    :role="tone === 'error' ? 'alert' : 'status'"
    :data-tone="tone"
    :style="{ display: 'flex', gap: '14px', padding: compact ? '10px 14px' : '16px', borderRadius: compact ? '18px' : '22px', alignItems: compact ? 'center' : 'flex-start' }"
  >
    <span :style="{ width: compact ? '32px' : '52px', height: compact ? '32px' : '52px', borderRadius: '50%', flex: 'none', display: 'grid', placeItems: 'center', background: t[3], color: t[2] }">
      <MdIcon :name="icon ?? t[1]" :size="compact ? 18 : 26" :stroke-width="2" />
    </span>
    <div style="flex:1;min-width:0;display:grid;gap:4px">
      <strong v-if="title" :style="{ fontSize: compact ? '15px' : '16px', lineHeight: '21px', fontWeight: 650, color: 'var(--text-primary)' }">{{ title }}</strong>
      <div v-if="$slots.default" style="font-size:14px;line-height:20px;color:var(--text-secondary)"><slot /></div>
    </div>
  </aside>
</template>
