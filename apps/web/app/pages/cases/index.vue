<script setup lang="ts">
import type { NavKey } from '~/lib/ds/nav'
import { caseCardView, caseStats, filterCases, homeSummary, listFilters, sortByUpdated, type CaseFilter } from '~/lib/mobile/viewModel'

const route = useRoute()
const store = useMobileCases()
const filter = useState<CaseFilter>('md-mobile-filter', () => 'all')
const tab = computed<NavKey>(() => {
  const value = String(route.query.tab ?? 'cases')
  return (['cases', 'reconstruction', 'search', 'journal'].includes(value) ? value : 'cases') as NavKey
})

onMounted(() => { void store.ensureLoaded() })

const summary = computed(() => homeSummary(store.cases.value))
const filters = computed(() => listFilters(store.cases.value))
const stats = computed(() => caseStats(store.cases.value))
const cards = computed(() => {
  const now = new Date()
  return sortByUpdated(filterCases(store.cases.value, filter.value))
    .map(c => caseCardView(c, store.numbers.value.get(c.case_id) ?? 0, now))
})

async function openCase(caseId: string): Promise<void> {
  const target = store.cases.value.find(c => c.case_id === caseId)
  store.lastCaseId.value = caseId
  await navigateTo({ path: `/cases/${caseId}`, query: { tab: target?.current_mode === 'search' ? 'search' : 'reconstruction' } })
}

async function changeTab(key: NavKey): Promise<void> {
  if (key === 'cases') {
    await navigateTo('/cases')
    return
  }
  const last = store.lastCaseId.value
  if (last && store.cases.value.some(c => c.case_id === last)) {
    await navigateTo({ path: `/cases/${last}`, query: { tab: key } })
    return
  }
  await navigateTo({ path: '/cases', query: { tab: key } })
}
</script>

<template>
  <div class="mm-screen" data-testid="screen-cases">
    <template v-if="tab === 'cases'">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
        <MdIconButton icon="arrow-left" label="Главный экран" @click="navigateTo('/')" />
        <MdIconButton icon="settings" label="Настройки" @click="navigateTo('/settings')" />
      </div>
      <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin:20px 0 16px">
        <div style="display:grid;gap:4px">
          <h1 style="margin:0;font-size:40px;line-height:44px;font-weight:700;letter-spacing:-0.02em">Дела</h1>
          <span style="font-size:15px;line-height:22px;color:#587196;font-variant-numeric:tabular-nums" data-testid="cases-summary">{{ summary.listSub }}</span>
        </div>
        <MdButton icon="plus" data-testid="cases-new" @click="navigateTo('/new')">Новое</MdButton>
      </div>
      <div class="mm-stats" style="margin-bottom:16px">
        <MdGlassCard v-for="st in stats" :key="st.label" :padding="14" :radius="18">
          <div style="display:grid;gap:4px"><span class="mm-stat-n">{{ st.n }}</span><span style="font-size:13px;line-height:18px;color:#587196;font-weight:500">{{ st.label }}</span></div>
        </MdGlassCard>
      </div>
      <div class="mm-case-grid" style="display:grid;gap:12px;align-content:start;padding-bottom:120px">
        <MdFilterChips v-model="filter" :options="filters" label="Фильтр дел" />
        <MdCaseCard
          v-for="k in cards"
          :key="k.id"
          :title="k.title"
          :case-id="k.caseId"
          :status="k.status"
          :place="k.place"
          :updated="k.updated"
          :counts="k.counts"
          :icon="k.icon"
          @open="openCase(k.id)"
        />
        <MdEmptyState v-if="cards.length === 0" icon="folder" title="Пока нет дел" body="Создайте первое дело, чтобы начать систематический поиск." />
        <div class="mm-privacy-line" style="padding-top:6px"><MdIcon name="shield-check" :size="16" /><span>Канонические данные дела хранятся на этом устройстве.</span></div>
      </div>
    </template>
    <div v-else style="padding:40px 0 120px" data-testid="no-case-selected">
      <MdEmptyState icon="folder" title="Дело не выбрано" body="Откройте дело в списке или создайте новое." />
      <div style="margin-top:12px"><MdButton size="lg" block @click="navigateTo('/cases')">К списку дел</MdButton></div>
    </div>
    <div class="mm-nav-dock">
      <MdBottomNav :active="tab" @change="changeTab" />
    </div>
  </div>
</template>
