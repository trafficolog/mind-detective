<script setup lang="ts">
import type { CaseV2, CommandEnvelope } from '~/lib/api/contracts'
import type { NavKey } from '~/lib/ds/nav'
import {
  afterCheckCommand, checkCommand, closeCommand, errorMessage, eventCommand, freeAccountCommand, MobileInputError,
  pauseToggleCommand, setModeCommand, statementCommand, targetCommand,
  type CheckInput, type EventInput, type StatementInput,
} from '~/lib/mobile/commands'
import {
  caseMeta, caseStatus, confirmedStatements, findCandidateId, formatCaseNumber, freeAccountText, isClosed, itemKind,
  journalStats, journalView, nextZone, plural, recStats, searchProgress, timelineView, zonesView,
} from '~/lib/mobile/viewModel'
import { vocab } from '~/lib/mobile/vocab'
import { exportCase } from '~/lib/storage/exportImport'

type Sheet = null | 'statement' | 'event' | 'zone' | 'check' | 'close' | 'menu' | 'confirm'

const route = useRoute()
const router = useRouter()
const store = useMobileCases()
const { settings } = useMobileSettings()
const dictation = useDictation()
const assistant = useAssistantProposal()

const caseId = computed(() => String(route.params.id ?? ''))
const loaded = ref(false)
const caseValue = computed<CaseV2 | null>(() => store.cases.value.find(c => c.case_id === caseId.value) ?? null)
const tab = computed<NavKey>(() => {
  const value = String(route.query.tab ?? '')
  if (value === 'reconstruction' || value === 'search' || value === 'journal') return value
  return caseValue.value?.current_mode === 'search' ? 'search' : 'reconstruction'
})

const error = ref<string | null>(null)
const sheet = ref<Sheet>(null)
const sheetKey = ref(0)
const checkPlace = ref('')
const checkResult = ref('not_found')
const busy = ref(false)
const faDraft = ref<string | null>(null)

onMounted(async () => {
  await store.ensureLoaded()
  loaded.value = true
  if (caseValue.value) store.lastCaseId.value = caseValue.value.case_id
})
onBeforeUnmount(() => dictation.stop(true))

const kind = computed(() => (caseValue.value ? itemKind(caseValue.value) : 'physical'))
const words = computed(() => vocab(kind.value))
const open = computed(() => Boolean(caseValue.value && !isClosed(caseValue.value)))
const outcomeTitle = computed(() => {
  const c = caseValue.value
  if (!c || !isClosed(c)) return ''
  return c.lifecycle === 'closed_found' ? `${c.item_label} — найдено` : 'Поиск завершён без результата'
})
const headerMode = computed(() => (!caseValue.value || isClosed(caseValue.value) ? 'closed' : caseValue.value.current_mode === 'search' ? 'search' : 'reconstruction'))
const number = computed(() => formatCaseNumber(store.numbers.value.get(caseId.value) ?? 0))

const timeline = computed(() => (caseValue.value ? timelineView(caseValue.value) : null))
const stats = computed(() => (caseValue.value ? recStats(caseValue.value) : { confirmed: 0, unknown: 0, contradiction: 0 }))
const statements = computed(() => (caseValue.value ? confirmedStatements(caseValue.value) : []))
const savedFa = computed(() => (caseValue.value ? freeAccountText(caseValue.value) : ''))
const faValue = computed(() => faDraft.value ?? savedFa.value)
const faClean = computed(() => faDraft.value === null || faDraft.value === savedFa.value)
const zones = computed(() => (caseValue.value ? zonesView(caseValue.value) : []))
const progress = computed(() => (caseValue.value ? searchProgress(caseValue.value) : { done: 0, total: 0 }))
const next = computed(() => (caseValue.value ? nextZone(caseValue.value) : null))
const checks = computed(() => (caseValue.value ? journalView(caseValue.value) : []))
const jStats = computed(() => (caseValue.value ? journalStats(caseValue.value) : { total: 0, repeats: 0, partial: 0 }))
const inSearch = computed(() => caseValue.value?.current_mode === 'search')
const recStatCards = computed(() => [
  { label: 'Подтверждено', n: stats.value.confirmed, icon: 'circle-check', color: 'var(--confirmed-fg)', variant: 'confirmed' as const },
  { label: 'Неизвестно', n: stats.value.unknown, icon: 'circle-help', color: 'var(--unknown-fg)', variant: 'unknown' as const },
  { label: 'Противоречия', n: stats.value.contradiction, icon: 'triangle-alert', color: 'var(--contradiction-fg)', variant: 'contradiction' as const },
])
const question = computed(() => (open.value && timeline.value?.firstUnknownTitle ? `Что вы помните о событии «${timeline.value.firstUnknownTitle}»?` : ''))
const showAssist = computed(() => open.value && (tab.value === 'reconstruction' || (tab.value === 'search' && inSearch.value)))
const assistantHint = computed(() => {
  if (settings.value.assistantOn && assistant.connected.value) return 'Запросите один следующий шаг. Ассистент предлагает, вы решаете.'
  if (settings.value.assistantOn) return 'Сервер n8n не подключён — предложение даст локальный контрольный список.'
  return 'Локальный контрольный список предложит следующий шаг. Онлайн-ассистента можно включить в настройках.'
})
const currentProposal = computed(() => assistant.forCase(caseValue.value?.case_id))

async function setTab(key: NavKey): Promise<void> {
  error.value = null
  if (key === 'cases') {
    await navigateTo('/cases')
    return
  }
  await router.replace({ query: { ...route.query, tab: key } })
}

function openSheet(name: Sheet): void {
  error.value = null
  sheetKey.value += 1
  sheet.value = name
}

function closeSheet(): void {
  dictation.stop(true)
  sheet.value = null
  error.value = null
}

function fail(caught: unknown): false {
  error.value = caught instanceof MobileInputError ? errorMessage(caught.code, kind.value) : store.messageFor(caught, caseValue.value)
  return false
}

async function run(build: (current: CaseV2) => CommandEnvelope): Promise<CaseV2 | false> {
  const current = caseValue.value
  if (!current || busy.value) return false
  busy.value = true
  try {
    const updated = await store.run(current, build(current))
    error.value = null
    return updated
  } catch (caught) {
    return fail(caught)
  } finally {
    busy.value = false
  }
}

async function saveFreeAccount(): Promise<void> {
  const text = faDraft.value
  if (text === null) return
  dictation.stop(true)
  if (await run(c => freeAccountCommand(c, text))) faDraft.value = null
}

async function goSearch(stay = false): Promise<void> {
  if (await run(c => setModeCommand(c, 'search')) && !stay) await setTab('search')
}

async function submitStatement(input: StatementInput): Promise<void> {
  if (await run(c => statementCommand(c, input))) closeSheet()
}

async function submitEvent(input: EventInput): Promise<void> {
  if (await run(c => eventCommand(c, input))) closeSheet()
}

async function submitZone(name: string): Promise<void> {
  if (await run(c => targetCommand(c, name))) closeSheet()
}

function openCheck(place: string, result = 'not_found'): void {
  if (!open.value) return
  checkPlace.value = place
  checkResult.value = result
  openSheet('check')
}

async function submitCheck(input: CheckInput): Promise<void> {
  const updated = await run(c => checkCommand(c, input))
  if (!updated) return
  const close = afterCheckCommand(updated, input.result)
  if (close) {
    try {
      await store.run(updated, close)
    } catch (caught) {
      fail(caught)
      return
    }
  }
  closeSheet()
  await setTab('journal')
}

async function submitClose(outcome: 'found' | 'closed', where: string): Promise<void> {
  if (await run(c => closeCommand(c, outcome, where))) closeSheet()
}

async function togglePause(): Promise<void> {
  if (await run(c => pauseToggleCommand(c))) closeSheet()
}

function exportCurrent(): void {
  const c = caseValue.value
  if (!c) return
  const link = document.createElement('a')
  link.href = URL.createObjectURL(exportCase(c))
  link.download = `mind-detective-${store.numbers.value.get(c.case_id) ?? 0}.json`
  link.click()
  setTimeout(() => URL.revokeObjectURL(link.href), 500)
}

async function confirmDelete(): Promise<void> {
  const c = caseValue.value
  if (!c) return
  await store.remove(c.case_id)
  sheet.value = null
  await navigateTo('/cases')
}

async function askAssistant(): Promise<void> {
  if (caseValue.value && open.value) await assistant.ask(caseValue.value)
}

async function acceptProposal(): Promise<void> {
  const proposal = currentProposal.value
  if (!proposal || !caseValue.value) return
  if (proposal.kind === 'check' && proposal.place) {
    const place = proposal.place
    if (!findCandidateId(caseValue.value, place) && !(await run(c => targetCommand(c, place)))) return
    assistant.dismiss()
    await setTab('search')
    return
  }
  assistant.dismiss()
  openSheet('statement')
}

async function dictateFa(): Promise<void> {
  await dictation.toggle('fa', faValue.value, (text) => { faDraft.value = text })
}
</script>

<template>
  <div class="mm-screen" data-testid="screen-case">
    <div v-if="!caseValue" style="padding:40px 0 120px">
      <MdEmptyState v-if="loaded" icon="folder" title="Дело не найдено" body="Возможно, оно было удалено с этого устройства." />
      <div v-if="loaded" style="margin-top:12px"><MdButton size="lg" block @click="navigateTo('/cases')">К списку дел</MdButton></div>
    </div>

    <div v-else style="display:grid;gap:14px;align-content:start;padding-bottom:120px">
      <MdCaseHeader
        :case-id="number"
        :title="caseValue.item_label"
        :mode="headerMode"
        :status="caseStatus(caseValue)"
        :meta="caseMeta(caseValue)"
        show-stepper
        @back="navigateTo('/cases')"
        @menu="openSheet('menu')"
      />
      <MdNotice v-if="error && !sheet" tone="error" :title="error" compact data-testid="case-error" />
      <MdNotice v-if="dictation.dictationError.value && !sheet" tone="error" :title="dictation.dictationError.value" compact />
      <MdNotice v-if="!open" tone="info" :title="outcomeTitle" data-testid="case-outcome">История остаётся локально в этом браузере, пока вы сами не удалите дело или данные сайта.</MdNotice>

      <!-- Реконструкция -->
      <template v-if="tab === 'reconstruction'">
        <div class="mm-stats" data-testid="rec-stats">
          <MdGlassCard v-for="st in recStatCards" :key="st.label" :variant="st.variant" :padding="14" :radius="18">
            <div style="display:grid;gap:6px">
              <MdIcon :name="st.icon" :size="20" :color="st.color" />
              <span style="font-size:26px;line-height:30px;font-weight:700;letter-spacing:-0.02em;font-variant-numeric:tabular-nums">{{ st.n }}</span>
              <span style="font-size:12px;line-height:16px;color:var(--text-primary);font-weight:500">{{ st.label }}</span>
            </div>
          </MdGlassCard>
        </div>
        <span style="font-size:13px;line-height:18px;color:#587196">Режим структурирует только ваш рассказ и подтверждённые сведения — он не устанавливает, где вещь на самом деле.</span>
        <MdSectionHeader icon="notebook-pen" title="Свободный рассказ" />
        <MdTextArea
          :model-value="faValue"
          placeholder="Расскажите последовательность событий своими словами…"
          hint="Текст сохраняется дословно"
          :rows="5"
          :readonly="!open"
          id="free-account"
          @update:model-value="v => { faDraft = v }"
        />
        <div v-if="open" :style="{ display: 'grid', gridTemplateColumns: dictation.available.value ? '1fr 1fr' : '1fr', gap: '10px' }">
          <MdButton v-if="dictation.available.value" variant="secondary" :icon="dictation.icon('fa')" block @click="dictateFa">{{ dictation.label('fa') }}</MdButton>
          <MdButton variant="secondary" icon="save" block :disabled="faClean || busy" data-testid="free-account-save" @click="saveFreeAccount">Сохранить</MdButton>
        </div>

        <MdSectionHeader icon="circle-check" title="Подтверждённые вами сведения" :meta="statements.length ? String(statements.length) : ''" />
        <MdGlassCard v-for="s in statements" :key="s.id" :variant="s.variant" :padding="14" data-testid="statement-card">
          <div style="display:grid;gap:8px">
            <span style="font-size:16px;line-height:22px;font-weight:600">{{ s.text }}</span>
            <span style="font-size:14px;line-height:20px;color:#587196">{{ s.sub }}</span>
            <div><MdStatusChip :status="s.chip" size="sm" /></div>
          </div>
        </MdGlassCard>
        <span v-if="statements.length === 0" style="font-size:15px;color:#587196">Пока нет отдельно подтверждённых сведений.</span>
        <MdButton v-if="open" variant="secondary" icon="plus" block data-testid="add-statement" @click="openSheet('statement')">Добавить сведение</MdButton>

        <MdSectionHeader icon="waypoints" title="Временная последовательность" :meta="timeline?.items.length ? plural(timeline.items.length, 'событие', 'события', 'событий') : ''" />
        <ol style="display:grid;gap:12px;padding:0;margin:0;list-style:none" data-testid="timeline">
          <MdTimelineEvent
            v-for="e in timeline?.items ?? []"
            :key="e.id"
            :time="e.time"
            :title="e.title"
            :detail="e.detail"
            :status="e.status"
            :connector="e.connector"
            icon="map-pin"
            source="Введено вами"
          />
        </ol>
        <span v-if="!timeline?.items.length" style="font-size:15px;color:#587196">Событий пока нет. Неизвестное — допустимое состояние.</span>
        <MdButton v-if="open" variant="secondary" icon="plus" block data-testid="add-event" @click="openSheet('event')">Добавить событие</MdButton>

        <MdStatePanel tone="unknown" title="Что остаётся неизвестным" :count="stats.unknown" data-testid="panel-unknown">Неизвестное — допустимое состояние. Интервал можно оставить неизвестным.</MdStatePanel>
        <MdStatePanel tone="contradiction" title="Противоречия в указанных данных" :count="stats.contradiction" data-testid="panel-contradiction">
          <div v-for="x in timeline?.contradictions ?? []" :key="x" style="font-size:14px;line-height:20px" data-testid="contradiction-line">{{ x }}</div>
          Приложение не выбирает версию за вас.
        </MdStatePanel>
        <MdStatePanel v-if="question" tone="hypothesis" title="Уточняющий вопрос">{{ question }} Ответ станет сведением только после вашего подтверждения.</MdStatePanel>
        <MdGlassCard v-if="open && !inSearch">
          <div style="display:grid;gap:12px">
            <strong style="font-size:18px;font-weight:650">Готовы перейти к проверкам?</strong>
            <span style="font-size:15px;line-height:22px;color:#587196">Переход явный: сведения останутся в деле, а следующий экран будет про проверки.</span>
            <MdButton size="lg" block icon-right="arrow-right" data-testid="go-search" @click="goSearch()">{{ words.goSearch }}</MdButton>
          </div>
        </MdGlassCard>
      </template>

      <!-- Поиск -->
      <template v-if="tab === 'search'">
        <template v-if="!inSearch">
          <MdEmptyState icon="search" title="Поиск ещё не начат" body="Проверки начинаются только по вашему явному действию." />
          <MdButton v-if="open" size="lg" block icon-right="arrow-right" data-testid="go-search-here" @click="goSearch(true)">{{ words.goSearch }}</MdButton>
        </template>
        <template v-else>
          <MdGlassCard v-if="progress.total > 0" :padding="20" data-testid="search-progress">
            <div style="display:grid;gap:16px">
              <MdWorkflowProgress :done="progress.done" :total="progress.total" unit="мест" label="Прогресс поиска" variant="segments" mode="search" />
              <template v-if="next">
                <div class="mm-divider" />
                <div style="display:flex;gap:14px;align-items:center">
                  <div class="mm-tile" style="width:48px;height:48px;border-radius:16px;background:#DDF3F6;color:#0A6E80"><MdIcon :name="kind === 'digital' ? 'image' : 'map-pin'" :size="24" /></div>
                  <div style="flex:1;display:grid;gap:2px"><span style="font-size:13px;line-height:18px;color:#587196">{{ words.next }}</span><strong style="font-size:19px;line-height:24px;font-weight:700" data-testid="next-zone">{{ next.name }}</strong></div>
                </div>
                <MdButton size="lg" block icon="search" data-testid="check-now" @click="openCheck(next.name)">Проверить сейчас</MdButton>
              </template>
            </div>
          </MdGlassCard>
          <MdNotice v-if="!next && open" tone="info" :title="zones.length ? (kind === 'digital' ? 'Все источники из списка проверены' : 'Все места из списка проверены') : (kind === 'digital' ? 'Добавьте источник, который хотите проверить' : 'Добавьте место, которое хотите проверить')" />
          <MdSectionHeader :icon="kind === 'digital' ? 'image' : 'map-pin'" :title="words.places" :meta="progress.total ? `${progress.done} из ${progress.total}` : ''" />
          <div v-for="z in zones" :key="z.id" data-testid="zone-row">
            <MdListRow :lead="z.n" :title="z.name" :subtitle="z.label" :icon="z.icon" chevron @click="openCheck(z.name)" />
          </div>
          <template v-if="open">
            <MdButton variant="secondary" icon="plus" block data-testid="add-zone" @click="openSheet('zone')">{{ words.addPlace }}</MdButton>
            <MdButton icon="circle-check" block data-testid="found" @click="openCheck(next?.name ?? zones[0]?.name ?? '', 'found')">Нашёл</MdButton>
            <MdButton variant="ghost" block data-testid="finish-unresolved" @click="openSheet('close')">Завершить без результата</MdButton>
          </template>
        </template>
      </template>

      <MobileAssistantCard
        v-if="showAssist"
        :proposal="currentProposal"
        :busy="assistant.busy.value"
        :words="words"
        :hint="assistantHint"
        @ask="askAssistant"
        @accept="acceptProposal"
        @dismiss="assistant.dismiss()"
      />

      <!-- Журнал -->
      <template v-if="tab === 'journal'">
        <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-top:4px">
          <h2 style="margin:0;font-size:28px;line-height:34px;font-weight:700;letter-spacing:-0.02em">Журнал проверок</h2>
          <span style="font-size:15px;color:#587196;font-variant-numeric:tabular-nums;padding-bottom:4px">{{ checks.length ? String(checks.length) : '' }}</span>
        </div>
        <div v-if="checks.length" class="mm-stats" data-testid="journal-stats">
          <MdGlassCard v-for="st in [{ label: 'Всего', n: jStats.total }, { label: 'Повторные', n: jStats.repeats }, { label: 'Неполные', n: jStats.partial }]" :key="st.label" :padding="14" :radius="18">
            <div style="display:grid;gap:4px"><span style="font-size:26px;line-height:30px;font-weight:700;letter-spacing:-0.02em;font-variant-numeric:tabular-nums">{{ st.n }}</span><span style="font-size:12px;line-height:16px;color:#587196;font-weight:500">{{ st.label }}</span></div>
          </MdGlassCard>
        </div>
        <MdSearchCheckCard
          v-for="k in checks"
          :key="k.id"
          :place="k.place"
          :method="k.method"
          :time="k.time"
          :result="k.result"
          :note="k.note"
          :repeat="k.repeat"
          :kind="kind"
        />
        <MdEmptyState v-if="!checks.length" icon="list-checks" title="Проверок пока нет" :body="words.emptyJournal" />
      </template>
    </div>

    <div class="mm-nav-dock">
      <MdBottomNav :active="tab" @change="setTab" />
    </div>

    <MobileStatementSheet v-if="sheet === 'statement'" :key="`st-${sheetKey}`" :error="error" @close="closeSheet" @submit="submitStatement" />
    <MobileEventSheet v-if="sheet === 'event'" :key="`ev-${sheetKey}`" :error="error" @close="closeSheet" @submit="submitEvent" />
    <MobileZoneSheet v-if="sheet === 'zone'" :key="`zn-${sheetKey}`" :words="words" :error="error" @close="closeSheet" @submit="submitZone" />
    <MobileCheckSheet v-if="sheet === 'check'" :key="`ck-${sheetKey}`" :words="words" :kind="kind" :place="checkPlace" :initial-result="checkResult" :error="error" @close="closeSheet" @submit="submitCheck" />
    <MobileCloseSheet v-if="sheet === 'close'" :key="`cl-${sheetKey}`" :words="words" :error="error" @close="closeSheet" @submit="submitClose" />
    <MobileMenuSheet v-if="sheet === 'menu' && caseValue" :title="caseValue.item_label" :open="open" :paused="caseValue.lifecycle === 'paused'" @close="closeSheet" @pause="togglePause" @finish="openSheet('close')" @export="exportCurrent" @remove="openSheet('confirm')" />
    <MobileConfirmSheet v-if="sheet === 'confirm'" title="Удалить это дело?" @close="closeSheet" @confirm="confirmDelete" />
  </div>
</template>
