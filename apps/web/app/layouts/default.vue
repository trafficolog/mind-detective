<script setup lang="ts">
// Offline-first: load every mobile route chunk up front so navigation works after the network drops
// (WebKit does not always route lazy chunk requests through the service worker cache).
const routesReady = ref(false)
onMounted(async () => {
  try {
    await Promise.all(['/new', '/cases', '/cases/offline-preload', '/settings'].map(path => preloadRouteComponents(path)))
  } finally {
    routesReady.value = true
  }
})
</script>

<template>
  <div class="mm-app" :data-routes-ready="routesReady ? 'true' : 'false'">
    <div class="mm-column">
      <slot />
    </div>
  </div>
</template>
