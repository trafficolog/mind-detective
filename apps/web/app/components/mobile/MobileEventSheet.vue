<script setup lang="ts">
import { maskClockInput } from '~/lib/mobile/timeMask'
import { PRECISIONS } from '~/lib/mobile/vocab'
import type { EventInput } from '~/lib/mobile/commands'

defineProps<{ error?: string | null }>()
const emit = defineEmits<{ submit: [input: EventInput], close: [] }>()
const title = ref('')
const precision = ref('exact')
const time = ref('')
const options = Object.entries(PRECISIONS).map(([value, label]) => ({ value, label }))

function onTime(event: Event): void {
  time.value = maskClockInput((event.target as HTMLInputElement).value)
  ;(event.target as HTMLInputElement).value = time.value
}
</script>

<template>
  <MdBottomSheet title="Добавить событие" @close="emit('close')">
    <div style="display:grid;gap:14px" data-testid="sheet-event">
      <MdTextArea v-model="title" label="Название события" placeholder="Например, кафе" :rows="1" id="event-title" />
      <MdChoiceGroup v-model="precision" label="Точность времени" :options="options" :columns="3" />
      <label v-if="precision !== 'unknown'" class="md-field"><span class="md-field__label">Время</span><input class="md-textarea mm-time-input" data-testid="event-time" type="text" inputmode="numeric" pattern="[0-9]*" maxlength="5" autocomplete="off" placeholder="ЧЧ:ММ" :value="time" @input="onTime"></label>
      <MdNotice v-if="error" tone="error" :title="error" compact />
      <MdButton size="lg" block :disabled="!title.trim()" data-testid="event-submit" @click="emit('submit', { title, precision, time })">Добавить событие</MdButton>
    </div>
  </MdBottomSheet>
</template>
