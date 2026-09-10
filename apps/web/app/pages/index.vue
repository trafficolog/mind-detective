<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'
import { importCase } from '~/lib/storage/exportImport'

const repository = useCaseRepository()
const api = useCaseApi()
const loading = ref(true)
const importPending = ref(false)
const importMessage = ref<string | null>(null)

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

async function handleImport(event: Event): Promise<void> {
  const input = event.currentTarget as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  importPending.value = true
  importMessage.value = null
  try {
    const imported = await importCase(file, api.validateCase)
    await repository.put(imported)
    importMessage.value = 'Импорт завершён. Дело сохранено локально.'
    await navigateTo(`/cases/${imported.case_id}`)
  } catch {
    importMessage.value = 'Не удалось импортировать дело: файл или версия схемы не поддерживается.'
  } finally {
    importPending.value = false
    input.value = ''
  }
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

    <aside class="privacy-note" data-testid="home-storage-actions">
      <strong>Локальные данные</strong>
      <p>Дела сохраняются в этом браузере. Облачной копии по умолчанию нет.</p>
      <label class="secondary-action" for="case-import" :aria-busy="importPending">
        {{ importPending ? 'Проверяем файл…' : 'Импортировать дело из JSON' }}
      </label>
      <input id="case-import" class="visually-hidden" data-testid="case-import" type="file" accept="application/json,.json" :disabled="importPending" @change="handleImport">
      <p v-if="importMessage" role="status">{{ importMessage }}</p>
    </aside>
  </main>
</template>
