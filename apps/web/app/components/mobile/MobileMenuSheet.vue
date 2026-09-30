<script setup lang="ts">
defineProps<{ title: string, open: boolean, paused: boolean }>()
const emit = defineEmits<{ pause: [], finish: [], export: [], remove: [], close: [] }>()
</script>

<template>
  <MdBottomSheet :title="title" @close="emit('close')">
    <div style="display:grid;gap:10px" data-testid="sheet-menu">
      <MdButton v-if="open" variant="secondary" block :icon="paused ? 'play' : 'pause'" data-testid="menu-pause" @click="emit('pause')">{{ paused ? 'Продолжить' : 'Приостановить' }}</MdButton>
      <MdButton v-if="open" variant="secondary" block icon="flag" data-testid="menu-finish" @click="emit('finish')">Закрыть дело</MdButton>
      <MdButton variant="secondary" block icon="download" data-testid="menu-export" @click="emit('export')">Экспортировать JSON</MdButton>
      <MdButton variant="danger" block icon="trash-2" data-testid="menu-delete" @click="emit('remove')">Удалить локальное дело</MdButton>
    </div>
  </MdBottomSheet>
</template>
