<script setup lang="ts">
import type { CaseV2, ExperimentalArm, ProposalModel } from '~/lib/api/contracts'

const props = defineProps<{
  caseValue: CaseV2
  arm: ExperimentalArm
  proposal: ProposalModel | null
  pending: boolean
}>()

const emit = defineEmits<{
  checked: []
  reject: []
  write: []
  journal: []
  found: []
}>()
</script>

<template>
  <article class="case-shell" data-testid="case-shell" :data-arm="arm">
    <header class="case-shell__header">
      <NuxtLink to="/" class="muted">← Все дела</NuxtLink>
      <h1>{{ props.caseValue.item_label }}</h1>
      <ModeBanner :mode="props.caseValue.current_mode" :arm="arm" />
    </header>
    <div class="case-shell__body">
      <ProgressStrip :case-value="props.caseValue" />
      <NextActionCard :proposal="proposal" :pending="pending" @checked="emit('checked')" @reject="emit('reject')" />
      <InteractionJournal :entries="props.caseValue.interaction_journal" />
      <InteractionDock :pending="pending" @write="emit('write')" @journal="emit('journal')" @found="emit('found')" />
    </div>
  </article>
</template>
