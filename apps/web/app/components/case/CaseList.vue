<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'

const props = defineProps<{
  cases: readonly CaseV2[]
}>()

const resumableCases = computed(() => props.cases.filter(caseValue => ['active', 'paused'].includes(caseValue.lifecycle)))
</script>

<template>
  <section v-if="resumableCases.length" class="case-list" aria-labelledby="recent-cases-title" data-testid="case-list">
    <div class="section-heading">
      <h2 id="recent-cases-title">Продолжить поиск</h2>
      <span>{{ resumableCases.length }}</span>
    </div>
    <NuxtLink
      v-for="caseValue in resumableCases"
      :key="caseValue.case_id"
      class="case-row"
      :to="`/cases/${caseValue.case_id}`"
      :data-testid="`case-row-${caseValue.case_id}`"
    >
      <span class="case-row__label">{{ caseValue.item_label }}</span>
      <span class="case-row__meta">
        {{ caseValue.lifecycle === 'paused' ? 'Приостановлено' : 'В процессе' }} ·
        {{ new Date(caseValue.updated_at).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' }) }}
      </span>
    </NuxtLink>
  </section>
</template>
