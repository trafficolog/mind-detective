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

const { t } = useCopy()
const isAction = computed(() => props.proposal?.kind === 'next_action' && Boolean(props.proposal.target))
</script>

<template>
  <section class="next-action-card" :aria-busy="pending" data-testid="next-action-card">
    <p class="eyebrow">{{ t('next.eyebrow') }}</p>
    <template v-if="proposal">
      <p
        class="next-action-card__copy"
        :data-testid="proposal.kind === 'need_more_information' ? 'need-more-information' : 'proposal-copy'"
      >
        {{ t(props.proposal.copy_key) }}
      </p>
      <p v-if="proposal.target" class="next-action-card__target" data-testid="next-action-target">
        {{ proposal.target }}
      </p>
      <div v-if="isAction" class="next-action-card__actions">
        <button class="primary-action" data-testid="mark-checked" type="button" :disabled="pending" :aria-busy="pending" @click="emit('checked')">
          {{ pending ? t('next.pending') : t('next.checked_not_found') }}
        </button>
        <button class="secondary-action" data-testid="reject-action" type="button" :disabled="pending" @click="emit('reject')">{{ t('next.reject') }}</button>
      </div>
    </template>
    <p v-else class="muted">{{ t('next.loading') }}</p>
  </section>
</template>
