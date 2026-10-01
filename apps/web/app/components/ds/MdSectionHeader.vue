<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  iconColor?: string
  title: string
  meta?: string
}>(), { icon: undefined, iconColor: 'var(--brand-600)', meta: undefined })
</script>

<template>
  <div style="display:flex;align-items:center;gap:10px;min-height:32px">
    <MdIcon v-if="icon" :name="icon" :size="22" :color="iconColor" />
    <h2 style="flex:1;font-size:18px;line-height:24px;font-weight:650">{{ title }}</h2>
    <span v-if="meta" style="font-size:15px;color:var(--text-secondary);font-variant-numeric:tabular-nums">{{ meta }}</span>
  </div>
</template>
