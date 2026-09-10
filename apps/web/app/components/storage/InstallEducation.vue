<script setup lang="ts">
interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}

const props = defineProps<{ engaged: boolean }>()
const installEvent = shallowRef<BeforeInstallPromptEvent | null>(null)
const installed = ref(false)

function capture(event: Event): void {
  event.preventDefault()
  installEvent.value = event as BeforeInstallPromptEvent
}

async function install(): Promise<void> {
  if (!installEvent.value) return
  await installEvent.value.prompt()
  const choice = await installEvent.value.userChoice
  if (choice.outcome === 'accepted') installed.value = true
  installEvent.value = null
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', capture)
  window.addEventListener('appinstalled', () => { installed.value = true }, { once: true })
})

onBeforeUnmount(() => window.removeEventListener('beforeinstallprompt', capture))
</script>

<template>
  <aside v-if="engaged && !installed" class="privacy-note" data-testid="install-education">
    <strong>Установить как приложение</strong>
    <p>Установка делает MIND Detective удобнее для повторного открытия, но не является облачной резервной копией ваших дел.</p>
    <button v-if="installEvent" class="secondary-action" type="button" data-testid="install-app" @click="install">Установить</button>
    <p v-else class="muted">Если кнопка установки недоступна, используйте меню браузера «Установить приложение» / «На экран Домой».</p>
  </aside>
</template>
