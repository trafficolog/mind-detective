<script setup lang="ts">
defineProps<{
  pending: boolean
}>()

const emit = defineEmits<{
  journal: []
  found: []
}>()
const { t } = useCopy()
</script>

<template>
  <nav class="interaction-dock" :aria-label="t('journal.title')" data-testid="interaction-dock">
    <button class="secondary-action" type="button" :disabled="pending" @click="emit('journal')">{{ t('dock.journal') }}</button>
    <button class="primary-action" data-testid="found-case" type="button" :disabled="pending" @click="emit('found')">{{ t('dock.found') }}</button>
  </nav>
</template>
