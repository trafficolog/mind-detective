<script setup lang="ts">
const props = defineProps<{
  savedText: string | null
  pending: boolean
}>()

const emit = defineEmits<{
  submit: [text: string]
}>()

const { t } = useCopy()
const draft = ref('')

function submit(): void {
  if (!draft.value.trim()) return
  emit('submit', draft.value)
}
</script>

<template>
  <section class="reconstruction-card" data-testid="free-account-card">
    <header class="reconstruction-card__heading">
      <span class="reconstruction-card__icon" aria-hidden="true">✎</span>
      <div>
        <p class="eyebrow">{{ t('reconstruction.free_account.label') }}</p>
        <h2>{{ t('reconstruction.free_account.title') }}</h2>
      </div>
    </header>
    <p class="reconstruction-card__help">{{ t('reconstruction.free_account.prompt') }}</p>

    <form v-if="props.savedText === null" class="reconstruction-form" @submit.prevent="submit">
      <textarea
        v-model="draft"
        data-testid="free-account-input"
        rows="6"
        :disabled="props.pending"
        :placeholder="t('reconstruction.free_account.placeholder')"
      />
      <button
        class="primary-action"
        data-testid="free-account-submit"
        type="submit"
        :disabled="props.pending || !draft.trim()"
      >
        {{ t('reconstruction.free_account.submit') }}
      </button>
    </form>

    <div v-else class="raw-account" data-testid="free-account-saved">
      <strong>{{ t('reconstruction.free_account.saved') }}</strong>
      <p>{{ props.savedText }}</p>
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
.reconstruction-card__heading p,
.raw-account p { margin: 0; }
.reconstruction-card__icon {
  display: inline-grid;
  place-items: center;
  min-width: 2rem;
  height: 2rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-weight: 800;
}
.reconstruction-card__help { margin: 0; color: var(--muted); }
.reconstruction-form { display: grid; gap: .75rem; }
textarea { width: 100%; box-sizing: border-box; min-height: 8rem; resize: vertical; }
.raw-account {
  display: grid;
  gap: .5rem;
  padding: 1rem;
  border: 1px dashed var(--line);
  border-radius: .75rem;
}
.raw-account p { white-space: pre-wrap; }
</style>
