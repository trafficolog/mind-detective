<script setup lang="ts">
import { computed, useAttrs } from 'vue'

withDefaults(defineProps<{
  lead?: string
  icon?: string
  iconColor?: string
  title: string
  subtitle?: string
  chevron?: boolean
  selected?: boolean
}>(), { lead: undefined, icon: undefined, iconColor: 'var(--brand-700)', subtitle: undefined, chevron: false, selected: false })

const attrs = useAttrs()
const tag = computed(() => (attrs.onClick ? 'button' : 'div'))
</script>

<template>
  <component :is="tag" :type="tag === 'button' ? 'button' : undefined" :class="['md-row', selected ? 'md-row--selected' : '']">
    <span v-if="lead !== undefined" class="md-row__lead" :style="selected ? { background: 'var(--brand-100)', color: 'var(--brand-700)' } : undefined">{{ lead }}</span>
    <MdIcon v-if="icon" :name="icon" :size="22" :color="iconColor" />
    <span class="md-row__body">
      <span class="md-row__title" :style="selected ? { fontWeight: 650 } : undefined">{{ title }}</span>
      <span v-if="subtitle" class="md-row__sub">{{ subtitle }}</span>
    </span>
    <slot name="trailing" />
    <MdIcon v-if="chevron" name="chevron-right" :size="20" color="var(--text-secondary)" />
  </component>
</template>
