<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'

const repository = useCaseRepository()
const loading = ref(true)

onMounted(async () => {
  try {
    await repository.refresh()
  } finally {
    loading.value = false
  }
})

async function handleCreated(caseValue: CaseV2): Promise<void> {
  await repository.put(caseValue)
  await navigateTo(`/cases/${caseValue.case_id}`)
}
</script>

<template>
  <main class="home-screen" data-testid="home-screen">
    <section class="hero-panel">
      <p class="eyebrow">MIND Detective</p>
      <h1>Ищите вещь системно, а не по кругу</h1>
      <p class="lede">
        Зафиксируем, что уже известно и проверено, затем выберем один полезный следующий шаг.
      </p>
      <CreateCaseForm @created="handleCreated" />
    </section>

    <p v-if="loading" class="muted" aria-live="polite">Загружаем локальные дела…</p>
    <CaseList v-else :cases="repository.cases.value" />

    <aside class="privacy-note">
      Дела сохраняются локально в этом браузере. Облачной копии по умолчанию нет.
    </aside>
  </main>
</template>
