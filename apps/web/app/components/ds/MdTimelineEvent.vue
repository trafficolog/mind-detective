<script setup lang="ts">
import { computed } from 'vue'

type Status = 'confirmed' | 'unknown' | 'contradiction' | 'hypothesis'
const props = withDefaults(defineProps<{
  time: string
  title: string
  detail?: string
  status?: Status
  source?: string
  icon?: string
  connector?: Status | 'none'
  chipLabel?: string
}>(), { detail: undefined, status: 'confirmed', source: undefined, icon: undefined, connector: undefined, chipLabel: undefined })

const NODE: Record<Status, [string, string, string]> = {
  confirmed: ['var(--brand-700)', 'rgba(255,255,255,.75)', 'var(--confirmed-fg)'],
  unknown: ['var(--unknown-fg)', 'var(--unknown-bg)', 'var(--unknown-fg)'],
  contradiction: ['var(--contradiction-fg)', 'var(--contradiction-bg)', 'var(--contradiction-fg)'],
  hypothesis: ['var(--hypothesis-fg)', 'var(--hypothesis-bg)', 'var(--hypothesis-fg)'],
}
const DEF_ICON: Record<Status, string> = { confirmed: 'map-pin', unknown: 'circle-help', contradiction: 'triangle-alert', hypothesis: 'lightbulb' }
const CHIP: Record<Status, string> = { confirmed: 'confirmed', unknown: 'unknown', contradiction: 'contradiction', hypothesis: 'question' }
const CARD: Record<Status, string> = { confirmed: 'md-glass', unknown: 'md-glass md-glass--unknown', contradiction: 'md-glass md-glass--contradiction', hypothesis: 'md-glass md-glass--secondary' }
const LINE: Record<Status, string> = { confirmed: '', unknown: ' md-tl__line--dashed', contradiction: ' md-tl__line--red', hypothesis: ' md-tl__line--muted' }

const node = computed(() => NODE[props.status])
const conn = computed(() => (props.connector === undefined ? props.status : props.connector))
const timeColor = computed(() => (props.status === 'unknown' ? 'var(--unknown-ink)' : props.status === 'contradiction' ? 'var(--contradiction-ink)' : 'var(--text-secondary)'))
</script>

<template>
  <li class="md-tl" style="list-style:none" :data-status="status">
    <div class="md-tl__rail">
      <span class="md-tl__node" :style="{ background: node[1], color: node[0] }">
        <MdIcon :name="icon ?? DEF_ICON[status]" :size="20" :stroke-width="2" />
        <span aria-hidden="true" :style="{ position: 'absolute', right: '-9px', top: '17px', width: '9px', height: '9px', borderRadius: '50%', background: node[2], boxShadow: '0 0 0 2px rgba(255,255,255,.9)' }" />
      </span>
      <span v-if="conn && conn !== 'none'" :class="'md-tl__line' + (LINE[conn as Status] ?? '')" />
    </div>
    <div :class="CARD[status]" :style="{ display: 'flex', gap: '12px', padding: '10px', borderRadius: '20px', alignItems: 'center', border: status === 'hypothesis' ? '1px dashed var(--hypothesis-line)' : undefined }">
      <span style="flex:1;min-width:0;display:grid;gap:3px;padding:4px 6px;justify-items:start">
        <span :style="{ fontSize: '14px', lineHeight: '18px', color: timeColor, fontWeight: status === 'confirmed' ? 400 : 600, fontVariantNumeric: 'tabular-nums' }">{{ time }}</span>
        <span style="font-size:17px;line-height:22px;font-weight:650;color:var(--text-primary)">{{ title }}</span>
        <span v-if="detail" style="font-size:14px;line-height:19px;color:var(--text-secondary)">{{ detail }}</span>
        <span style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:4px">
          <MdStatusChip :status="CHIP[status]" :label="chipLabel" size="sm" />
          <span v-if="source" style="font-size:12px;line-height:16px;color:var(--text-secondary)">{{ source }}</span>
        </span>
      </span>
    </div>
  </li>
</template>
