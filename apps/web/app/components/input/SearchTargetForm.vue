<script setup lang="ts">
const props = defineProps<{
  pending: boolean
}>()

const emit = defineEmits<{
  submit: [target: string]
}>()

const { t } = useCopy()
const target = ref('')

function submitTarget(): void {
  const value = target.value.trim()
  if (!value || props.pending) return
  emit('submit', value)
  target.value = ''
}
</script>

<template>
  <form class="privacy-note" data-testid="search-target-form" @submit.prevent="submitTarget">
    <label class="field-label" for="search-target-input">{{ t('search_target.label') }}</label>
    <p class="muted">{{ t('search_target.help') }}</p>
    <input
      id="search-target-input"
      v-model="target"
      data-testid="search-target-input"
      name="search-target"
      type="text"
      autocomplete="off"
      :placeholder="t('search_target.placeholder')"
      :disabled="pending"
      required
    >
    <button
      class="secondary-action"
      data-testid="add-search-target"
      type="submit"
      :disabled="pending || !target.trim()"
    >
      {{ pending ? t('search_target.pending') : t('search_target.add') }}
    </button>
  </form>
</template>
