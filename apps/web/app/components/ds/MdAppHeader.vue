<script setup lang="ts">
withDefaults(defineProps<{
  logoSrc?: string
  subtitle?: string
  showSettings?: boolean
}>(), { logoSrc: undefined, subtitle: 'Системный поиск потерянного', showSettings: false })
defineEmits<{ settings: [] }>()
</script>

<template>
  <header style="display:flex;align-items:center;gap:12px">
    <img v-if="logoSrc" :src="logoSrc" alt="" width="52" height="52" style="flex:none;object-fit:contain">
    <div style="flex:1;min-width:0">
      <div style="font-size:26px;line-height:30px;letter-spacing:-0.015em;white-space:nowrap;color:var(--text-primary)">
        <span style="font-weight:800">Mind</span> <span style="font-weight:500">Detective</span>
      </div>
      <div v-if="subtitle" style="font-size:13px;line-height:18px;color:var(--text-secondary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ subtitle }}</div>
    </div>
    <slot name="trailing" />
    <MdIconButton v-if="showSettings" icon="settings" label="Настройки" :size="48" @click="$emit('settings')" />
  </header>
</template>
