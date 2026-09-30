<script setup lang="ts">
import type { NavKey } from '~/lib/ds/nav'
const NAV_ITEMS: Array<[NavKey, string, string]> = [
  ['cases', 'folder', 'Дела'],
  ['reconstruction', 'waypoints', 'Реконструкция'],
  ['search', 'search', 'Поиск'],
  ['journal', 'list-checks', 'Журнал'],
]
defineProps<{ active: NavKey }>()
defineEmits<{ change: [key: NavKey] }>()
</script>

<template>
  <nav class="md-nav" aria-label="Основная навигация">
    <button
      v-for="[k, ic, l] in NAV_ITEMS"
      :key="k"
      type="button"
      class="md-nav__item"
      :data-nav="k"
      :aria-current="active === k ? 'page' : undefined"
      @click="$emit('change', k)"
    >
      <MdIcon :name="ic" :size="26" :stroke-width="active === k ? 2.1 : 1.8" />
      <span>{{ l }}</span>
    </button>
  </nav>
</template>
