<script setup lang="ts">
import type { CaseV2, ProposalModel } from '~/lib/api/contracts'

const props = defineProps<{
  caseValue: CaseV2
  proposal: ProposalModel | null
  pending: boolean
}>()

const emit = defineEmits<{
  checked: []
  reject: []
  write: []
  journal: []
  found: []
  pause: []
}>()
</script>

<template>
  <article class="case-shell" data-testid="case-shell">
    <header class="case-shell__header">
      <div class="section-heading">
        <NuxtLink to="/" class="muted">← Все дела</NuxtLink>
        <button
          v-if="props.caseValue.lifecycle === 'active'"
          class="secondary-action"
          data-testid="pause-case"
          type="button"
          :disabled="pending"
          @click="emit('pause')"
        >
          Приостановить
        </button>
      </div>
      <h1>{{ props.caseValue.item_label }}</h1>
      <ModeBanner :mode="props.caseValue.current_mode" />
    </header>
    <div class="case-shell__body">
      <ProgressStrip :case-value="props.caseValue" />
      <NextActionCard :proposal="proposal" :pending="pending" @checked="emit('checked')" @reject="emit('reject')" />
      <InteractionJournal :entries="props.caseValue.interaction_journal" />
      <InteractionDock :pending="pending" @write="emit('write')" @journal="emit('journal')" @found="emit('found')" />
    </div>
  </article>
</template>
