<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'

defineProps<{ caseValue: CaseV2 }>()
const { t } = useCopy()
</script>

<template>
  <section class="hero-panel" data-testid="case-outcome">
    <p class="eyebrow">{{ t('outcome.eyebrow') }}</p>
    <h1 v-if="caseValue.lifecycle === 'closed_found'">{{ t('outcome.found', { item: caseValue.item_label }) }}</h1>
    <h1 v-else>{{ t('outcome.unresolved') }}</h1>
    <p class="lede">{{ t('outcome.retained') }}</p>
    <NuxtLink class="primary-action" to="/">{{ t('case.to_list') }}</NuxtLink>
  </section>
</template>
