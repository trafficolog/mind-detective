<script setup lang="ts">
import type { ActionFeedbackV2 } from '~/lib/api/contracts'

const props = defineProps<{ target: string; pending: boolean }>()
const emit = defineEmits<{
  close: []
  reject: [reason: ActionFeedbackV2['reason']]
}>()

const reason = ref<ActionFeedbackV2['reason']>('irrelevant')
const { dialogRef, onDialogKeydown } = useDialogFocus(() => emit('close'))
</script>

<template>
  <div class="dialog-backdrop" data-testid="action-reject-dialog" @click.self="emit('close')">
    <section
      ref="dialogRef"
      class="dialog-sheet"
      role="dialog"
      aria-modal="true"
      aria-labelledby="reject-title"
      tabindex="-1"
      @keydown="onDialogKeydown"
    >
      <p class="eyebrow">Следующий шаг</p>
      <h2 id="reject-title">Почему «{{ props.target }}» сейчас не подходит?</h2>
      <label class="field-label" for="reject-reason">Причина</label>
      <select id="reject-reason" v-model="reason" data-testid="reject-reason">
        <option value="already_checked">Уже достаточно проверено</option>
        <option value="impossible_now">Сейчас невозможно проверить</option>
        <option value="irrelevant">Не относится к моей ситуации</option>
        <option value="unsafe_or_uncomfortable">Небезопасно или некомфортно</option>
        <option value="other">Другая причина</option>
      </select>
      <div class="dialog-actions">
        <button class="secondary-action" type="button" :disabled="pending" @click="emit('close')">Отмена</button>
        <button class="primary-action" data-testid="confirm-reject" type="button" :disabled="pending" @click="emit('reject', reason)">Выбрать другой шаг</button>
      </div>
    </section>
  </div>
</template>
