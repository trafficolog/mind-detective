<script setup lang="ts">
withDefaults(defineProps<{ icon?: string, title: string, body?: string }>(), { icon: 'folder-open', body: undefined })
</script>

<template>
  <div data-testid="empty-state" style="display:grid;justify-items:center;text-align:center;gap:14px;padding:32px 20px">
    <span style="width:96px;height:96px;border-radius:30px;display:grid;place-items:center;background:linear-gradient(160deg,rgba(255,255,255,.8),rgba(220,238,255,.7));border:1px solid var(--line-glass);box-shadow:var(--shadow-glass);color:var(--brand-600)">
      <MdIcon :name="icon" :size="40" :stroke-width="1.75" />
    </span>
    <h2 style="font-size:22px;line-height:28px;font-weight:650">{{ title }}</h2>
    <p v-if="body" style="font-size:15px;line-height:22px;color:var(--text-secondary);max-width:300px">{{ body }}</p>
    <div v-if="$slots.default" style="display:grid;gap:10px;width:100%;max-width:320px;margin-top:6px"><slot /></div>
  </div>
</template>
