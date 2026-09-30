<script setup lang="ts">
import { methodsFor, RESULTS, type ItemKind, type KindVocabulary } from '~/lib/mobile/vocab'
import type { CheckInput } from '~/lib/mobile/commands'

const props = defineProps<{ words: KindVocabulary, kind: ItemKind, place: string, initialResult: string, error?: string | null }>()
const emit = defineEmits<{ submit: [input: CheckInput], close: [] }>()
const dictation = useDictation()
const methodOptions = computed(() => Object.entries(methodsFor(props.kind)).map(([value, label]) => ({ value, label })))
const resultOptions = Object.entries(RESULTS).map(([value, label]) => ({ value, label }))
const method = ref(Object.keys(methodsFor(props.kind))[0]!)
const result = ref(props.initialResult)
const note = ref('')

function close(): void {
  dictation.stop(true)
  emit('close')
}
function submit(): void {
  dictation.stop(true)
  emit('submit', { place: props.place, method: method.value, result: result.value, note: note.value })
}
</script>

<template>
  <MdBottomSheet :title="words.check" :subtitle="place" @close="close">
    <div style="display:grid;gap:14px" data-testid="sheet-check">
      <MdChoiceGroup v-model="method" label="Способ проверки" :options="methodOptions" />
      <MdChoiceGroup v-model="result" label="Результат" :options="resultOptions" :columns="1" />
      <MdTextArea v-model="note" label="Заметка" :rows="2" id="check-note" />
      <MdButton v-if="dictation.available.value" variant="secondary" size="sm" :icon="dictation.icon('note')" block @click="dictation.toggle('note', note, v => { note = v })">{{ dictation.label('note') }}</MdButton>
      <MdNotice v-if="error || dictation.dictationError.value" tone="error" :title="error || dictation.dictationError.value || ''" compact />
      <MdButton size="lg" block data-testid="check-submit" @click="submit">Сохранить проверку</MdButton>
    </div>
  </MdBottomSheet>
</template>
