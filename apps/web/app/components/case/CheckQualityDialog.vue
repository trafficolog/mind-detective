<script setup lang="ts">
import type { SearchMethod } from '~/lib/api/contracts'

const props = defineProps<{
  checkId: string
  target: string
  initialInaccessibleParts: readonly string[]
  pending: boolean
}>()

const emit = defineEmits<{
  close: []
  refine: [payload: { checkId: string; method: Exclude<SearchMethod, 'reported_check' | 'inaccessible'>; inaccessibleParts: string[] }]
}>()

const method = ref<Exclude<SearchMethod, 'reported_check' | 'inaccessible'>>('visual_systematic')
const inaccessibleText = ref(props.initialInaccessibleParts.join(', '))

function submit(): void {
  emit('refine', {
    checkId: props.checkId,
    method: method.value,
    inaccessibleParts: inaccessibleText.value.split(',').map(part => part.trim()).filter(Boolean),
  })
}
</script>

<template>
  <div class="dialog-backdrop" data-testid="check-quality-dialog" @click.self="emit('close')">
    <section class="dialog-sheet" role="dialog" aria-modal="true" aria-labelledby="quality-title">
      <p class="eyebrow">Уточнение проверки</p>
      <h2 id="quality-title">Как именно вы проверяли «{{ target }}»?</h2>
      <p class="muted">Это уточнение появилось только потому, что тот же шаг снова стал полезным для решения.</p>
      <label class="field-label" for="check-method">Способ проверки</label>
      <select id="check-method" v-model="method" data-testid="check-method">
        <option value="glance">Быстро посмотрел</option>
        <option value="visual_systematic">Осмотрел системно</option>
        <option value="empty_and_check">Освободил и проверил содержимое</option>
        <option value="tactile">Проверил руками</option>
      </select>
      <label class="field-label" for="inaccessible-parts">Что осталось недоступным? Это отдельно от качества проверки.</label>
      <input id="inaccessible-parts" v-model="inaccessibleText" data-testid="inaccessible-parts" placeholder="Например, закрытый внутренний карман">
      <div class="dialog-actions">
        <button class="secondary-action" type="button" :disabled="pending" @click="emit('close')">Не сейчас</button>
        <button class="primary-action" data-testid="save-check-quality" type="button" :disabled="pending" @click="submit">Сохранить уточнение</button>
      </div>
    </section>
  </div>
</template>
