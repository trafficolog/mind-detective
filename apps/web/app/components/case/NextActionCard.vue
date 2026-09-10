<script setup lang="ts">
import type { ProposalModel } from '~/lib/api/contracts'

const props = defineProps<{
  proposal: ProposalModel | null
  pending: boolean
}>()

const emit = defineEmits<{
  checked: []
  reject: []
}>()

const isAction = computed(() => props.proposal?.kind === 'next_action' && Boolean(props.proposal.target))
</script>

<template>
  <section class="next-action-card" :aria-busy="pending" data-testid="next-action-card">
    <p class="eyebrow">Следующий шаг</p>
    <template v-if="proposal">
      <p v-if="proposal.kind === 'need_more_information'" class="next-action-card__target" data-testid="need-more-information">
        Нужно ещё немного подтверждённой информации
      </p>
      <p v-else-if="proposal.kind === 'clarification'" class="next-action-card__target">
        Уточним последовательность перед следующим шагом
      </p>
      <p v-else-if="proposal.target" class="next-action-card__target" data-testid="next-action-target">
        {{ proposal.target }}
      </p>
      <p v-else class="next-action-card__target">Продолжим с безопасного следующего шага</p>
      <div v-if="isAction" class="next-action-card__actions">
        <button class="primary-action" data-testid="mark-checked" type="button" :disabled="pending" :aria-busy="pending" @click="emit('checked')">
          {{ pending ? 'Сохраняем…' : 'Проверил' }}
        </button>
        <button class="secondary-action" data-testid="reject-action" type="button" :disabled="pending" @click="emit('reject')">Не подходит</button>
      </div>
    </template>
    <p v-else class="muted">Готовим следующий шаг…</p>
  </section>
</template>
