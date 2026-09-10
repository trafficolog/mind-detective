<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'

defineProps<{ caseValue: CaseV2 }>()
</script>

<template>
  <section class="hero-panel" data-testid="case-outcome">
    <p class="eyebrow">Дело завершено</p>
    <h1 v-if="caseValue.lifecycle === 'closed_found'">{{ caseValue.item_label }} — найдено</h1>
    <h1 v-else>Поиск завершён без результата</h1>
    <p class="lede">
      История остаётся локально в этом браузере, пока вы сами не удалите дело или данные сайта.
    </p>
    <NuxtLink class="primary-action" to="/">К списку дел</NuxtLink>
  </section>
</template>
