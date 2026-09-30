<script setup lang="ts">
defineProps<{ title: string }>()
const emit = defineEmits<{ confirm: [], close: [] }>()
</script>

<template>
  <MdBottomSheet :title="title" subtitle="Восстановить можно будет только из ранее экспортированного JSON." @close="emit('close')">
    <div style="display:grid;gap:10px" data-testid="sheet-confirm">
      <MdButton variant="danger" size="lg" block data-testid="confirm-delete" @click="emit('confirm')">Да, удалить</MdButton>
      <MdButton variant="ghost" block @click="emit('close')">Отмена</MdButton>
    </div>
  </MdBottomSheet>
</template>
