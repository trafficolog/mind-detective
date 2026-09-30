<script setup lang="ts">
import { computed } from 'vue'

// DS_CHANGES §1: digital methods and `kind` (image tile for digital sources).
const METHODS: Record<string, [string, string]> = {
  'visual': ['eye', 'Визуально'],
  'hand': ['hand', 'Руками'],
  'flashlight': ['flashlight', 'С фонариком'],
  'opened': ['package-open', 'Открыл отсек'],
  'moved': ['move', 'Переместил предметы'],
  'asked': ['users', 'Спросил человека'],
  'name-search': ['search', 'Поиск по названию'],
  'date-filter': ['calendar', 'Фильтр по дате'],
  'browsed': ['folder-open', 'Просмотрел папку или альбом'],
  'trash': ['trash-2', '«Удалённые» / корзина'],
  'shared': ['message-square', 'Переписка и отправленные'],
  'other': ['ellipsis', 'Другое'],
}

const props = withDefaults(defineProps<{
  place: string
  method?: string
  time?: string
  result?: string
  note?: string
  repeat?: boolean
  kind?: 'physical' | 'digital'
}>(), { method: 'visual', time: undefined, result: 'not-found', note: undefined, repeat: false, kind: 'physical' })

const m = computed(() => METHODS[props.method] ?? METHODS.other!)
</script>

<template>
  <div class="md-glass" data-testid="search-check-card" style="display:flex;gap:12px;padding:10px;border-radius:20px;align-items:center">
    <span style="width:52px;height:52px;border-radius:16px;flex:none;display:grid;place-items:center;background:var(--mode-search-bg);color:var(--mode-search-fg)">
      <MdIcon :name="kind === 'digital' ? 'image' : 'map-pin'" :size="22" />
    </span>
    <span style="flex:1;min-width:0;display:grid;gap:3px">
      <span style="display:flex;gap:8px;align-items:baseline">
        <span style="flex:1;min-width:0;font-size:17px;line-height:22px;font-weight:650;color:var(--text-primary)">{{ place }}</span>
        <span v-if="time" style="font-size:13px;color:var(--text-secondary);white-space:nowrap;font-variant-numeric:tabular-nums">{{ time }}</span>
      </span>
      <span v-if="note" style="font-size:14px;line-height:19px;color:var(--text-primary)">{{ note }}</span>
      <span style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">
        <span class="md-chip md-chip--sm" style="background:rgba(255,255,255,.7);color:var(--text-secondary);border:1px solid var(--line-soft)">
          <MdIcon :name="m[0]" :size="14" /> {{ m[1] }}
        </span>
        <MdStatusChip :status="result" size="sm" />
        <MdStatusChip v-if="repeat && result !== 'repeat'" status="repeat" label="Повторная" size="sm" />
      </span>
    </span>
  </div>
</template>
