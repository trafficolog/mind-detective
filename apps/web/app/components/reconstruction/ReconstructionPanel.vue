<script setup lang="ts">
import type { CaseV2, RebuildTimelinePayload, StatementV2 } from '~/lib/api/contracts'
import { freeAccountText, hasFreeAccount } from '~/composables/useReconstruction'

const props = defineProps<{
  caseValue: CaseV2
  pending: boolean
}>()

const emit = defineEmits<{
  recordFreeAccount: [text: string]
  addStatement: [payload: Record<string, unknown>]
  rebuildTimeline: [payload: RebuildTimelinePayload]
  switchToSearch: []
}>()

const { t } = useCopy()
const hasAccount = computed(() => hasFreeAccount(props.caseValue))
const accountText = computed(() => freeAccountText(props.caseValue))
const structuredStatements = computed<StatementV2[]>(() => props.caseValue.statements.filter(statement => (
  statement.source === 'user' && statement.statement_type !== 'search_suggestion'
)))
</script>

<template>
  <section class="reconstruction-panel" data-testid="reconstruction-panel">
    <header class="reconstruction-panel__intro">
      <p class="eyebrow">{{ t('reconstruction.mode_label') }}</p>
      <h1>{{ t('reconstruction.title') }}</h1>
      <p class="scope-note">
        <span aria-hidden="true">ⓘ</span>
        <span>{{ t('reconstruction.scope') }}</span>
      </p>
    </header>

    <FreeAccountCard
      :saved-text="accountText"
      :pending="props.pending"
      @submit="emit('recordFreeAccount', $event)"
    />

    <template v-if="hasAccount">
      <section class="reconstruction-card" data-testid="structured-evidence">
        <header class="structured-heading">
          <span aria-hidden="true">✓</span>
          <div>
            <p class="eyebrow">{{ t('reconstruction.statement.confirmed') }}</p>
            <h2>{{ t('reconstruction.statement.saved_title') }}</h2>
          </div>
        </header>
        <ol v-if="structuredStatements.length" class="evidence-list">
          <li v-for="statement in structuredStatements" :key="statement.id">
            <strong>{{ statement.original_text }}</strong>
            <span v-if="statement.event_time">{{ statement.event_time }}</span>
            <span v-for="limitation in statement.limitations" :key="limitation">{{ limitation }}</span>
          </li>
        </ol>
        <p v-else class="muted">{{ t('reconstruction.statement.empty') }}</p>
      </section>

      <StatementCapture :pending="props.pending" @submit="emit('addStatement', $event)" />
      <TimelineEditor
        :statements="structuredStatements"
        :timeline="props.caseValue.timeline"
        :pending="props.pending"
        @rebuild="emit('rebuildTimeline', $event)"
      />
      <TimelineSummary v-if="props.caseValue.timeline" :timeline="props.caseValue.timeline" />
    </template>

    <div class="transition-card">
      <div>
        <strong>{{ t('reconstruction.search_transition.title') }}</strong>
        <p>{{ t('reconstruction.search_transition.help') }}</p>
      </div>
      <button
        class="primary-action"
        data-testid="switch-to-search"
        type="button"
        :disabled="props.pending"
        @click="emit('switchToSearch')"
      >
        {{ t('reconstruction.to_search') }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.reconstruction-panel { display: grid; gap: 1rem; }
.reconstruction-panel__intro { display: grid; gap: .5rem; }
.reconstruction-panel__intro h1,
.reconstruction-panel__intro p { margin: 0; }
.scope-note {
  display: flex;
  gap: .6rem;
  align-items: flex-start;
  padding: .9rem 1rem;
  border: 1px solid var(--line);
  border-radius: .75rem;
}
.reconstruction-card,
.transition-card {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid var(--line);
  border-radius: 1rem;
  background: var(--panel);
}
.structured-heading { display: flex; gap: .75rem; align-items: flex-start; }
.structured-heading h2,
.structured-heading p,
.transition-card p { margin: 0; }
.evidence-list { display: grid; gap: .7rem; margin: 0; padding-left: 1.3rem; }
.evidence-list li { display: grid; gap: .2rem; }
.evidence-list span { color: var(--muted); font-size: .92rem; }
.transition-card { align-items: center; }
@media (min-width: 720px) {
  .transition-card { grid-template-columns: 1fr auto; }
}
</style>
