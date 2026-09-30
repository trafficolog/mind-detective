<script setup lang="ts">
import type { KindVocabulary } from '~/lib/mobile/vocab'

const props = defineProps<{ words: KindVocabulary, error?: string | null }>()
const emit = defineEmits<{ submit: [outcome: 'found' | 'closed', where: string], close: [] }>()
const outcome = ref<'found' | 'closed'>('closed')
const where = ref('unknown')
const outcomeOptions = computed(() => [{ value: 'found', label: props.words.found }, { value: 'closed', label: 'Завершить без результата' }])
const whereOptions = computed(() => [
  { value: 'current', label: 'На текущем предложенном шаге' },
  { value: 'elsewhere', label: props.words.elsewhere },
  { value: 'previous', label: 'Там, где уже проверял раньше' },
  { value: 'unknown', label: 'Не уверен / не хочу уточнять' },
])
</script>

<template>
  <MdBottomSheet title="Чем закончился поиск?" @close="emit('close')">
    <div style="display:grid;gap:14px" data-testid="sheet-close">
      <MdChoiceGroup :model-value="outcome" :options="outcomeOptions" :columns="1" @update:model-value="v => { outcome = v as 'found' | 'closed' }" />
      <MdChoiceGroup v-if="outcome === 'found'" v-model="where" label="Где относительно плана?" :options="whereOptions" :columns="1" />
      <MdNotice v-if="error" tone="error" :title="error" compact />
      <MdButton size="lg" block data-testid="close-submit" @click="emit('submit', outcome, where)">Завершить дело</MdButton>
      <MdButton variant="ghost" block @click="emit('close')">Продолжить поиск</MdButton>
    </div>
  </MdBottomSheet>
</template>
