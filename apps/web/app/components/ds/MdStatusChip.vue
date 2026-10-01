<script setup lang="ts">
import { computed } from 'vue'
import { STATUS_MAP, TONES } from '~/lib/ds/statusMap'

const props = withDefaults(defineProps<{
  status?: string
  label?: string
  size?: 'md' | 'sm'
  icon?: string
}>(), { status: 'confirmed', label: undefined, size: 'md', icon: undefined })

const entry = computed(() => STATUS_MAP[props.status] ?? STATUS_MAP.confirmed!)
const tone = computed(() => TONES[entry.value[0]]!)
const iconName = computed(() => props.icon ?? entry.value[1])
</script>

<template>
  <span :class="['md-chip', `md-chip--${size}`]" :data-status="status" :style="{ background: tone[0], color: tone[1] }">
    <span v-if="iconName === 'dot'" class="md-chip__dot" :style="{ background: tone[2] }" />
    <MdIcon v-else :name="iconName" :size="size === 'sm' ? 14 : 16" :stroke-width="2.1" :color="tone[2]" />
    <span>{{ label ?? entry[2] }}</span>
  </span>
</template>
