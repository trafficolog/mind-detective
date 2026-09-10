<script setup lang="ts">
export type FoundContext = 'current_suggested_action' | 'elsewhere_unplanned' | 'after_previous_check' | 'unknown'

const props = defineProps<{
  pending: boolean
}>()

const emit = defineEmits<{
  close: []
  found: [context: FoundContext]
  unresolved: []
}>()

const context = ref<FoundContext>('current_suggested_action')
const { dialogRef, onDialogKeydown } = useDialogFocus(() => emit('close'))
</script>

<template>
  <div class="dialog-backdrop" data-testid="close-case-dialog" @click.self="emit('close')">
    <section
      ref="dialogRef"
      class="dialog-sheet"
      role="dialog"
      aria-modal="true"
      aria-labelledby="close-title"
      tabindex="-1"
      @keydown="onDialogKeydown"
    >
      <p class="eyebrow">Завершение дела</p>
      <h2 id="close-title">Чем закончился поиск?</h2>
      <label class="field-label" for="found-context">Если вещь найдена — где относительно плана?</label>
      <select id="found-context" v-model="context" data-testid="found-context">
        <option value="current_suggested_action">На текущем предложенном шаге</option>
        <option value="elsewhere_unplanned">В другом, незапланированном месте</option>
        <option value="after_previous_check">Там, где уже проверял раньше</option>
        <option value="unknown">Не уверен / не хочу уточнять</option>
      </select>
      <div class="dialog-actions">
        <button class="secondary-action" type="button" :disabled="pending" @click="emit('close')">Продолжить поиск</button>
        <button class="primary-action" data-testid="close-found" type="button" :disabled="pending" @click="emit('found', context)">Вещь найдена</button>
        <button class="secondary-action" data-testid="close-unresolved" type="button" :disabled="pending" @click="emit('unresolved')">Завершить без результата</button>
      </div>
    </section>
  </div>
</template>
