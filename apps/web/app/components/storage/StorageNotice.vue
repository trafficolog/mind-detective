<script setup lang="ts">
import { requestPersistentStorage } from '~/lib/storage/indexeddb'

type PersistenceState = 'idle' | 'granted' | 'denied' | 'unsupported'

const props = defineProps<{ engaged: boolean }>()
const state = ref<PersistenceState>('idle')
const requested = ref(false)

async function requestPersistence(): Promise<void> {
  if (requested.value || !props.engaged) return
  requested.value = true
  const result = await requestPersistentStorage()
  state.value = result
  localStorage.setItem('mind-detective:persistence-state', result)
}

onMounted(() => {
  const previous = localStorage.getItem('mind-detective:persistence-state')
  if (previous === 'granted' || previous === 'denied' || previous === 'unsupported') {
    state.value = previous
    requested.value = true
  }
  if (props.engaged && !requested.value) void requestPersistence()
})

watch(() => props.engaged, engaged => {
  if (engaged && !requested.value) void requestPersistence()
})
</script>

<template>
  <aside class="privacy-note" data-testid="storage-notice">
    <strong>Локальное хранение</strong>
    <p>Дела хранятся в этом браузере. Облачной резервной копии в 0.2.0 нет; очистка данных сайта может удалить дела.</p>
    <p v-if="state === 'granted'">Браузер разрешил постоянное хранилище, но экспорт всё равно остаётся способом резервного восстановления.</p>
    <p v-else-if="state === 'denied'">Браузер не гарантирует защиту данных от автоматического удаления. Для важных дел используйте экспорт.</p>
    <p v-else-if="state === 'unsupported'">Этот браузер не сообщает о постоянном хранилище. Для важных дел используйте экспорт.</p>
    <p v-else class="muted">После первого полезного действия приложение запросит у браузера более устойчивое локальное хранение.</p>
  </aside>
</template>
