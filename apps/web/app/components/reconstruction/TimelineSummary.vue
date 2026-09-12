<script setup lang="ts">
import type { TimelineV2 } from '~/lib/api/contracts'

const props = defineProps<{
  timeline: TimelineV2
}>()

const { t } = useCopy()
</script>

<template>
  <section class="reconstruction-card" data-testid="timeline-summary">
    <header class="reconstruction-card__heading">
      <span class="reconstruction-card__icon" aria-hidden="true">≡</span>
      <div>
        <p class="eyebrow">{{ t('reconstruction.timeline.system_derived') }}</p>
        <h2>{{ t('reconstruction.timeline.summary_title') }}</h2>
      </div>
    </header>

    <div class="summary-block">
      <h3>{{ t('reconstruction.timeline.events') }}</h3>
      <ol v-if="props.timeline.events.length">
        <li v-for="event in props.timeline.events" :key="event.id">
          <strong>{{ event.label }}</strong>
          <span>{{ event.event_time ?? t('reconstruction.timeline.time_unknown') }}</span>
        </li>
      </ol>
      <p v-else class="muted">{{ t('reconstruction.timeline.empty') }}</p>
    </div>

    <div class="summary-block" data-testid="timeline-unknowns">
      <h3>{{ t('reconstruction.timeline.unknowns') }}</h3>
      <ul v-if="props.timeline.unknown_intervals.length">
        <li v-for="unknown in props.timeline.unknown_intervals" :key="unknown">{{ unknown }}</li>
      </ul>
      <p v-else class="muted">{{ t('reconstruction.timeline.empty') }}</p>
    </div>

    <div class="summary-block" data-testid="timeline-contradictions">
      <h3>{{ t('reconstruction.timeline.contradictions') }}</h3>
      <ul v-if="props.timeline.contradictions.length">
        <li v-for="contradiction in props.timeline.contradictions" :key="contradiction">{{ contradiction }}</li>
      </ul>
      <p v-else class="muted">{{ t('reconstruction.timeline.empty') }}</p>
    </div>
  </section>
</template>

<style scoped>
.reconstruction-card {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid var(--line);
  border-radius: 1rem;
  background: var(--panel);
}
.reconstruction-card__heading { display: flex; gap: .75rem; align-items: flex-start; }
.reconstruction-card__heading h2,
.reconstruction-card__heading p { margin: 0; }
.reconstruction-card__icon {
  display: inline-grid;
  place-items: center;
  min-width: 2rem;
  height: 2rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-weight: 800;
}
.summary-block { display: grid; gap: .5rem; padding-top: .75rem; border-top: 1px solid var(--line); }
.summary-block h3,
.summary-block p,
.summary-block ul,
.summary-block ol { margin: 0; }
.summary-block ul,
.summary-block ol { display: grid; gap: .35rem; padding-left: 1.3rem; }
.summary-block li { overflow-wrap: anywhere; }
.summary-block li span { display: block; color: var(--muted); }
</style>
