<script setup lang="ts">
import type { KindVocabulary } from '~/lib/mobile/vocab'

defineProps<{ words: KindVocabulary, error?: string | null }>()
const emit = defineEmits<{ submit: [name: string], close: [] }>()
const name = ref('')
</script>

<template>
  <MdBottomSheet :title="words.addPlace" :subtitle="words.addPlaceSub" @close="emit('close')">
    <div style="display:grid;gap:14px" data-testid="sheet-zone">
      <MdTextArea v-model="name" :placeholder="words.placeHint" :rows="1" id="zone-name" />
      <MdNotice v-if="error" tone="error" :title="error" compact />
      <MdButton size="lg" block :disabled="!name.trim()" data-testid="zone-submit" @click="emit('submit', name)">Добавить в список</MdButton>
    </div>
  </MdBottomSheet>
</template>
