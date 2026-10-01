<script setup lang="ts">
import { maskClockInput } from '~/lib/mobile/timeMask'
import { STATEMENT_TYPES } from '~/lib/mobile/vocab'
import type { StatementInput } from '~/lib/mobile/commands'

defineProps<{ error?: string | null }>()
const emit = defineEmits<{ submit: [input: StatementInput], close: [] }>()
const dictation = useDictation()
const type = ref('recollection')
const text = ref('')
const time = ref('')
const limitation = ref('')
const options = Object.entries(STATEMENT_TYPES).map(([value, label]) => ({ value, label }))

function onTime(event: Event): void {
  time.value = maskClockInput((event.target as HTMLInputElement).value)
  ;(event.target as HTMLInputElement).value = time.value
}
function close(): void {
  dictation.stop(true)
  emit('close')
}
function submit(): void {
  dictation.stop(true)
  emit('submit', { type: type.value, text: text.value, time: time.value, limitation: limitation.value })
}
</script>

<template>
  <MdBottomSheet title="Добавить сведение" subtitle="Подтверждено пользователем" @close="close">
    <div style="display:grid;gap:14px" data-testid="sheet-statement">
      <MdChoiceGroup v-model="type" label="Тип сведения" :options="options" />
      <MdNotice v-if="error || dictation.dictationError.value" tone="error" :title="error || dictation.dictationError.value || ''" compact />
      <MdTextArea v-model="text" label="Что вы сами помните или наблюдали?" :rows="3" id="statement-text" />
      <MdButton v-if="dictation.available.value" variant="secondary" size="sm" :icon="dictation.icon('text')" block @click="dictation.toggle('text', text, v => { text = v })">{{ dictation.label('text') }}</MdButton>
      <label class="md-field"><span class="md-field__label">Время события, если известно</span><input class="md-textarea mm-time-input" data-testid="statement-time" type="text" inputmode="numeric" pattern="[0-9]*" maxlength="5" autocomplete="off" placeholder="ЧЧ:ММ" :value="time" @input="onTime"></label>
      <MdTextArea v-model="limitation" label="Ограничение или неопределённость" :rows="1" id="statement-limitation" />
      <MdButton size="lg" block :disabled="!text.trim()" data-testid="statement-submit" @click="submit">Подтвердить и добавить</MdButton>
    </div>
  </MdBottomSheet>
</template>
