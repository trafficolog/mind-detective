<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  caseId: string
  title: string
  mode?: 'reconstruction' | 'search' | 'closed'
  status?: string
  meta?: string
  showStepper?: boolean
}>(), { mode: 'reconstruction', status: undefined, meta: undefined, showStepper: false })
defineEmits<{ back: [], menu: [] }>()

const STEPS: Array<[string, string, string]> = [['reconstruction', 'waypoints', 'Реконструкция'], ['search', 'search', 'Поиск'], ['closed', 'circle-check', 'Итог']]
const idx = computed(() => (props.mode === 'reconstruction' ? 0 : props.mode === 'search' ? 1 : 2))
const chip = computed(() => props.status ?? (props.mode === 'search' ? 'search' : props.mode === 'reconstruction' ? 'reconstruction' : 'closed'))
function col(i: number, k: string): string {
  return i === idx.value ? (k === 'search' ? 'var(--mode-search-fg)' : 'var(--brand-600)') : 'var(--nav-inactive)'
}
function bg(i: number, k: string): string {
  return i === idx.value ? (k === 'search' ? 'var(--mode-search-bg)' : 'var(--brand-100)') : 'rgba(255,255,255,.6)'
}
</script>

<template>
  <header style="display:grid;gap:14px">
    <div style="display:flex;align-items:center;gap:12px">
      <MdIconButton icon="chevron-left" label="Назад" @click="$emit('back')" />
      <span style="flex:1;font-size:15px;color:var(--text-secondary);font-weight:500">Дело {{ caseId }}</span>
      <MdIconButton icon="ellipsis" label="Действия с делом" @click="$emit('menu')" />
    </div>
    <div style="display:flex;gap:16px;align-items:center">
      <div style="display:grid;gap:8px;min-width:0;justify-items:start">
        <h1 style="font-size:30px;line-height:36px;font-weight:700;letter-spacing:-0.02em">{{ title }}</h1>
        <MdStatusChip :status="chip" />
        <span v-if="meta" style="font-size:14px;line-height:20px;color:var(--text-secondary)">{{ meta }}</span>
      </div>
    </div>
    <ol v-if="showStepper" aria-label="Этапы дела" style="list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center">
      <template v-for="([k, ic, l], i) in STEPS" :key="k">
        <MdIcon v-if="i > 0" name="arrow-right" :size="20" color="var(--text-tertiary)" />
        <li :aria-current="i === idx ? 'step' : undefined" style="display:grid;justify-items:center;gap:4px">
          <span :style="{ width: '44px', height: '44px', borderRadius: '50%', display: 'grid', placeItems: 'center', background: bg(i, k), color: col(i, k), border: '1px solid var(--line-glass)' }">
            <MdIcon :name="ic" :size="20" />
          </span>
          <span :style="{ fontSize: '13px', lineHeight: '16px', fontWeight: i === idx ? 650 : 500, color: col(i, k) }">{{ l }}</span>
        </li>
      </template>
    </ol>
  </header>
</template>
