<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

const props = withDefaults(defineProps<{ title?: string, subtitle?: string }>(), { title: undefined, subtitle: undefined })
const emit = defineEmits<{ close: [] }>()
const sheet = ref<HTMLElement | null>(null)
let previous: Element | null = null

function onKey(event: KeyboardEvent): void {
  if (event.key === 'Escape') emit('close')
}

onMounted(async () => {
  previous = document.activeElement
  document.addEventListener('keydown', onKey)
  await nextTick()
  sheet.value?.focus({ preventScroll: true })
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKey)
  if (previous instanceof HTMLElement) previous.focus({ preventScroll: true })
})
void props
</script>

<template>
  <div class="md-sheet-scrim" style="position:fixed" data-testid="bottom-sheet" @click.self="emit('close')">
    <section ref="sheet" class="md-sheet" role="dialog" aria-modal="true" :aria-label="title" tabindex="-1">
      <div class="md-sheet__grip" aria-hidden="true" />
      <div v-if="title" style="display:flex;align-items:flex-start;gap:12px;margin-bottom:16px">
        <div style="flex:1;min-width:0;display:grid;gap:4px">
          <h2 style="font-size:22px;line-height:28px;font-weight:650;letter-spacing:-0.01em">{{ title }}</h2>
          <p v-if="subtitle" style="font-size:15px;line-height:21px;color:var(--text-secondary)">{{ subtitle }}</p>
        </div>
        <MdIconButton icon="x" label="Закрыть" @click="emit('close')" />
      </div>
      <div style="display:grid;gap:16px"><slot /></div>
    </section>
  </div>
</template>
