<script setup lang="ts">
defineProps<{ pending: boolean }>()
const emit = defineEmits<{
  write: []
  journal: []
  found: []
}>()
</script>

<template>
  <nav class="interaction-dock" aria-label="Действия дела" data-testid="interaction-dock">
    <button class="secondary-action" type="button" :disabled="pending" @click="emit('journal')">Журнал</button>
    <button class="secondary-action" type="button" :disabled="pending" @click="emit('write')">Написать</button>
    <button class="primary-action" type="button" :disabled="pending" @click="emit('found')">Нашёл</button>
  </nav>
</template>
