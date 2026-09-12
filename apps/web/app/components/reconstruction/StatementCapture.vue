<script setup lang="ts">
const props = defineProps<{
  pending: boolean
}>()

const emit = defineEmits<{
  submit: [payload: Record<string, unknown>]
}>()

const { t } = useCopy()
const statementType = ref<'recollection' | 'habit' | 'observation' | 'hypothesis'>('recollection')
const text = ref('')
const eventTime = ref('')
const unknownTime = ref(false)
const limitation = ref('')

function normalizedDateTime(value: string): string | null {
  if (!value) return null
  return value.length === 16 ? `${value}:00` : value
}

function submit(): void {
  if (!text.value.trim()) return
  emit('submit', {
    statement_id: crypto.randomUUID(),
    source: 'user',
    statement_type: statementType.value,
    original_text: text.value,
    event_time: unknownTime.value ? null : normalizedDateTime(eventTime.value),
    user_confirmation: true,
    supporting_evidence_ids: [],
    limitations: limitation.value.trim() ? [limitation.value.trim()] : [],
  })
}
</script>

<template>
  <section class="reconstruction-card" data-testid="statement-capture">
    <header class="reconstruction-card__heading">
      <span class="reconstruction-card__icon" aria-hidden="true">✓</span>
      <div>
        <p class="eyebrow">{{ t('reconstruction.statement.confirmed') }}</p>
        <h2>{{ t('reconstruction.statement.title') }}</h2>
      </div>
    </header>

    <form class="reconstruction-form" @submit.prevent="submit">
      <label>
        <span>{{ t('reconstruction.statement.type') }}</span>
        <select v-model="statementType" data-testid="statement-type" :disabled="props.pending">
          <option value="recollection">{{ t('reconstruction.statement.type.recollection') }}</option>
          <option value="habit">{{ t('reconstruction.statement.type.habit') }}</option>
          <option value="observation">{{ t('reconstruction.statement.type.observation') }}</option>
          <option value="hypothesis">{{ t('reconstruction.statement.type.hypothesis') }}</option>
        </select>
      </label>

      <label>
        <span>{{ t('reconstruction.statement.text') }}</span>
        <textarea v-model="text" data-testid="statement-text" rows="3" :disabled="props.pending" />
      </label>

      <label>
        <span>{{ t('reconstruction.statement.event_time') }}</span>
        <input
          v-model="eventTime"
          data-testid="statement-event-time"
          type="datetime-local"
          :disabled="props.pending || unknownTime"
        />
      </label>

      <label class="check-row">
        <input v-model="unknownTime" data-testid="statement-unknown-time" type="checkbox" :disabled="props.pending" />
        <span>{{ t('reconstruction.statement.unknown_time') }}</span>
      </label>

      <label>
        <span>{{ t('reconstruction.statement.limitation') }}</span>
        <input v-model="limitation" data-testid="statement-limitation" type="text" :disabled="props.pending" />
      </label>

      <button class="primary-action" data-testid="statement-submit" type="submit" :disabled="props.pending || !text.trim()">
        {{ t('reconstruction.statement.submit') }}
      </button>
    </form>
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
.reconstruction-form { display: grid; gap: .9rem; }
label { display: grid; gap: .35rem; font-weight: 700; }
input, select, textarea { width: 100%; box-sizing: border-box; }
textarea { resize: vertical; }
.check-row { display: flex; align-items: center; gap: .5rem; font-weight: 600; }
.check-row input { width: auto; }
</style>
