<script setup lang="ts">
withDefaults(defineProps<{
  title: string
  caseId: string
  icon?: string
  status?: string
  place?: string
  updated?: string
  counts?: string[]
}>(), { icon: 'package', status: 'reconstruction', place: undefined, updated: undefined, counts: () => [] })

const emit = defineEmits<{ open: [] }>()
function key(event: KeyboardEvent): void {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    emit('open')
  }
}
</script>

<template>
  <div
    class="md-glass md-glass--interactive"
    role="link"
    tabindex="0"
    data-testid="case-card"
    style="padding:14px;display:flex;gap:14px;align-items:stretch"
    @click="emit('open')"
    @keydown="key"
  >
    <span style="width:104px;min-height:112px;border-radius:18px;flex:none;display:grid;place-items:center;background:linear-gradient(160deg,var(--brand-50),var(--brand-100));color:var(--brand-600)">
      <MdIcon :name="icon" :size="36" />
    </span>
    <div style="flex:1;min-width:0;display:grid;gap:7px;align-content:start">
      <div style="display:flex;align-items:center;gap:6px;color:var(--text-secondary);font-size:13px;line-height:18px">
        <MdIcon name="folder" :size="14" />
        <span style="flex:1">Дело {{ caseId }}</span>
      </div>
      <div style="font-size:18px;line-height:24px;font-weight:650;color:var(--text-primary)">{{ title }}</div>
      <div><MdStatusChip :status="status" size="sm" /></div>
      <div v-if="place" style="display:flex;gap:6px;align-items:flex-start;font-size:14px;line-height:19px">
        <MdIcon name="map-pin" :size="16" color="var(--text-secondary)" style="margin-top:2px" />
        <span>
          <span style="color:var(--text-primary)">{{ place }}</span>
          <span v-if="updated" style="display:block;color:var(--text-secondary);font-size:13px">{{ updated }}</span>
        </span>
      </div>
      <div v-if="counts.length" style="display:flex;flex-wrap:wrap;gap:4px 12px;font-size:13px;line-height:18px;color:var(--text-secondary);font-variant-numeric:tabular-nums">
        <span v-for="(c, i) in counts" :key="i">{{ c }}</span>
      </div>
    </div>
    <MdIcon name="chevron-right" :size="20" color="var(--text-secondary)" style="align-self:center" />
  </div>
</template>
