<script setup lang="ts">
import { vocab, type ItemKind } from '~/lib/mobile/vocab'

const route = useRoute()
const store = useMobileCases()
const dictation = useDictation()
const kind = ref<ItemKind>('physical')
const title = ref('')
const error = ref<string | null>(null)
const pending = ref(false)
const words = computed(() => vocab(kind.value))
const kindOptions = [{ value: 'physical', label: 'Вещь' }, { value: 'digital', label: 'Фото или файл' }]
const shownError = computed(() => error.value ?? dictation.dictationError.value)

onMounted(() => {
  void store.ensureLoaded()
  if (route.query.voice === '1' && dictation.available.value) void dictate()
})
onBeforeUnmount(() => dictation.stop(true))

async function dictate(): Promise<void> {
  await dictation.toggle('title', title.value, (text) => { title.value = text })
}

async function create(mode: 'reconstruction' | 'search'): Promise<void> {
  if (pending.value) return
  error.value = null
  if (!title.value.trim()) {
    error.value = 'Введите название.'
    return
  }
  pending.value = true
  dictation.stop(true)
  try {
    const created = await store.create(title.value, kind.value, mode)
    await navigateTo({ path: `/cases/${created.case_id}`, query: { tab: mode } })
  } catch (caught) {
    error.value = store.messageFor(caught)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="mm-screen" data-testid="screen-new" style="gap:16px;padding-bottom:28px">
    <div><MdIconButton icon="arrow-left" label="Назад" @click="navigateTo('/')" /></div>
    <div style="display:grid;gap:8px;margin-top:8px">
      <span class="mm-overline">Шаг 1 из 2</span>
      <h1 style="margin:0;font-size:34px;line-height:40px;font-weight:700;letter-spacing:-0.02em">Что потерялось?</h1>
    </div>
    <MdGlassCard :padding="16">
      <div style="display:grid;gap:12px">
        <MdChoiceGroup v-model="kind" label="Что ищем" :options="kindOptions" :columns="2" />
        <MdTextArea v-model="title" :placeholder="words.titleHint" :rows="1" id="new-case-title" />
        <MdButton v-if="dictation.available.value" variant="secondary" size="sm" :icon="dictation.icon('title')" block data-testid="dictate-title" @click="dictate">{{ dictation.label('title') }}</MdButton>
      </div>
    </MdGlassCard>
    <MdNotice v-if="shownError" tone="error" :title="shownError" compact />
    <div style="display:grid;gap:8px;margin-top:8px">
      <span class="mm-overline mm-overline--muted">Шаг 2 из 2 · с чего начать</span>
    </div>
    <MdGlassCard variant="interactive" :padding="16" data-testid="create-reconstruction" @click="create('reconstruction')">
      <div style="display:flex;gap:14px;align-items:center;text-align:left">
        <div class="mm-tile" style="width:48px;height:48px;border-radius:16px;background:#E3F1FF;color:#0B86EA"><MdIcon name="waypoints" :size="24" /></div>
        <div style="flex:1;display:grid;gap:3px"><strong style="font-size:17px;line-height:22px;font-weight:650">Восстановить события</strong><span style="font-size:14px;line-height:20px;color:#587196">Рассказ, подтверждённые сведения, временная линия</span></div>
        <MdIcon name="chevron-right" :size="20" color="#587196" />
      </div>
    </MdGlassCard>
    <MdGlassCard variant="interactive" :padding="16" data-testid="create-search" @click="create('search')">
      <div style="display:flex;gap:14px;align-items:center;text-align:left">
        <div class="mm-tile" style="width:48px;height:48px;border-radius:16px;background:#DDF3F6;color:#0A6E80"><MdIcon name="search" :size="24" /></div>
        <div style="flex:1;display:grid;gap:3px"><strong style="font-size:17px;line-height:22px;font-weight:650">Сразу к поиску</strong><span style="font-size:14px;line-height:20px;color:#587196">Места или источники и журнал проверок</span></div>
        <MdIcon name="chevron-right" :size="20" color="#587196" />
      </div>
    </MdGlassCard>
    <div style="flex:1" />
    <span style="font-size:13px;line-height:18px;color:#587196;text-align:center">Режим можно сменить позже. Переход к поиску — только по вашему действию.</span>
  </div>
</template>
