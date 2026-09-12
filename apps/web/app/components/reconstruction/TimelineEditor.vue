<script setup lang="ts">
import type { RebuildTimelinePayload, StatementV2, TimelineEventV2, TimelineV2 } from '~/lib/api/contracts'
import { buildRebuildTimelinePayload } from '~/composables/useReconstruction'

const props = defineProps<{
  statements: StatementV2[]
  timeline: TimelineV2 | null
  pending: boolean
}>()

const emit = defineEmits<{
  rebuild: [payload: RebuildTimelinePayload]
}>()

const { t } = useCopy()
const events = ref<TimelineEventV2[]>(structuredClone(props.timeline?.events ?? []))
const eventLabel = ref('')
const eventStatementId = ref('')
const eventTime = ref('')
const eventPrecision = ref('approximate')
const lastSupported = ref(props.timeline?.last_supported_interaction_id ?? '')
const firstMissing = ref(props.timeline?.first_noticed_missing_id ?? '')

watch(
  () => props.timeline,
  (timeline) => {
    if (!timeline) return
    events.value = structuredClone(timeline.events)
    lastSupported.value = timeline.last_supported_interaction_id ?? ''
    firstMissing.value = timeline.first_noticed_missing_id ?? ''
  },
  { deep: true },
)

function normalizedDateTime(value: string): string | null {
  if (!value) return null
  return value.length === 16 ? `${value}:00` : value
}

function addEvent(): void {
  if (!eventLabel.value.trim() || !eventStatementId.value) return
  events.value.push({
    id: crypto.randomUUID(),
    label: eventLabel.value.trim(),
    statement_ids: [eventStatementId.value],
    event_time: normalizedDateTime(eventTime.value),
    time_precision: eventPrecision.value,
  })
  eventLabel.value = ''
  eventStatementId.value = ''
  eventTime.value = ''
  eventPrecision.value = 'approximate'
}

function plainEvents(): TimelineEventV2[] {
  return events.value.map(event => ({
    id: event.id,
    label: event.label,
    statement_ids: [...event.statement_ids],
    event_time: event.event_time,
    time_precision: event.time_precision,
  }))
}

function rebuild(): void {
  emit('rebuild', buildRebuildTimelinePayload(
    plainEvents(),
    lastSupported.value || null,
    firstMissing.value || null,
  ))
}
</script>

<template>
  <section class="reconstruction-card" data-testid="timeline-editor">
    <header class="reconstruction-card__heading">
      <span class="reconstruction-card__icon" aria-hidden="true">↔</span>
      <div>
        <p class="eyebrow">{{ t('reconstruction.timeline.input_label') }}</p>
        <h2>{{ t('reconstruction.timeline.title') }}</h2>
      </div>
    </header>
    <p class="muted">{{ t('reconstruction.timeline.help') }}</p>

    <div class="timeline-form">
      <label>
        <span>{{ t('reconstruction.timeline.event_label') }}</span>
        <input v-model="eventLabel" data-testid="timeline-event-label" type="text" :disabled="props.pending" />
      </label>
      <label>
        <span>{{ t('reconstruction.timeline.event_statement') }}</span>
        <select v-model="eventStatementId" data-testid="timeline-event-statement" :disabled="props.pending">
          <option value="">—</option>
          <option v-for="statement in props.statements" :key="statement.id" :value="statement.id">
            {{ statement.original_text }}
          </option>
        </select>
      </label>
      <label>
        <span>{{ t('reconstruction.timeline.event_time') }}</span>
        <input v-model="eventTime" data-testid="timeline-event-time" type="datetime-local" :disabled="props.pending" />
      </label>
      <label>
        <span>{{ t('reconstruction.timeline.precision') }}</span>
        <select v-model="eventPrecision" data-testid="timeline-event-precision" :disabled="props.pending">
          <option value="exact">{{ t('reconstruction.timeline.precision.exact') }}</option>
          <option value="approximate">{{ t('reconstruction.timeline.precision.approximate') }}</option>
          <option value="unknown">{{ t('reconstruction.timeline.precision.unknown') }}</option>
        </select>
      </label>
      <button
        class="secondary-action"
        data-testid="timeline-add-event"
        type="button"
        :disabled="props.pending || !eventLabel.trim() || !eventStatementId"
        @click="addEvent"
      >
        {{ t('reconstruction.timeline.add_event') }}
      </button>
    </div>

    <ol v-if="events.length" class="timeline-events" data-testid="timeline-events">
      <li v-for="event in events" :key="event.id">
        <strong>{{ event.label }}</strong>
        <span>{{ event.event_time ?? t('reconstruction.timeline.time_unknown') }}</span>
      </li>
    </ol>

    <div class="anchor-grid">
      <label>
        <span>{{ t('reconstruction.timeline.last_supported') }}</span>
        <select v-model="lastSupported" data-testid="timeline-last-supported" :disabled="props.pending">
          <option value="">—</option>
          <option v-for="statement in props.statements" :key="statement.id" :value="statement.id">
            {{ statement.original_text }}
          </option>
        </select>
      </label>
      <label>
        <span>{{ t('reconstruction.timeline.first_missing') }}</span>
        <select v-model="firstMissing" data-testid="timeline-first-missing" :disabled="props.pending">
          <option value="">—</option>
          <option v-for="statement in props.statements" :key="statement.id" :value="statement.id">
            {{ statement.original_text }}
          </option>
        </select>
      </label>
    </div>

    <button class="primary-action" data-testid="timeline-rebuild" type="button" :disabled="props.pending" @click="rebuild">
      {{ t('reconstruction.timeline.rebuild') }}
    </button>
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
.reconstruction-card__heading p,
.muted { margin: 0; }
.reconstruction-card__icon {
  display: inline-grid;
  place-items: center;
  min-width: 2rem;
  height: 2rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-weight: 800;
}
.timeline-form,
.anchor-grid { display: grid; gap: .8rem; }
label { display: grid; gap: .35rem; font-weight: 700; }
input, select { width: 100%; box-sizing: border-box; }
.timeline-events { display: grid; gap: .5rem; margin: 0; padding-left: 1.3rem; }
.timeline-events li { display: grid; gap: .15rem; }
.timeline-events span { color: var(--muted); }
@media (min-width: 720px) {
  .timeline-form { grid-template-columns: 1.3fr 1.5fr 1fr 1fr; align-items: end; }
  .timeline-form .secondary-action { grid-column: 1 / -1; justify-self: start; }
  .anchor-grid { grid-template-columns: 1fr 1fr; }
}
</style>
