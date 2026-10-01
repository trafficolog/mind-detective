<script setup lang="ts">
import logoMark from '~/assets/brand/logo-mark.svg'
import { homeSummary } from '~/lib/mobile/viewModel'

const { settings, update } = useMobileSettings()
const store = useMobileCases()
const step = ref<'splash' | 'onb'>('splash')

onMounted(() => { void store.ensureLoaded() })

const summary = computed(() => homeSummary(store.cases.value))
const onbItems = [
  { icon: 'notebook-pen', title: 'Рассказ дословно', body: 'Ваш рассказ сохраняется как есть и не становится фактом автоматически.' },
  { icon: 'waypoints', title: 'Подтверждённое и неизвестное', body: 'Неизвестные интервалы и противоречия остаются на виду.' },
  { icon: 'search', title: 'Проверки по шагам', body: 'Вещь, фото или файл: журнал хранит место или источник, способ и результат каждой проверки.' },
]

function finishOnboarding(): void {
  update({ onboarded: true })
}

async function openActive(): Promise<void> {
  const active = summary.value.active
  if (!active) return
  store.lastCaseId.value = active.case_id
  await navigateTo({ path: `/cases/${active.case_id}`, query: { tab: active.current_mode === 'search' ? 'search' : 'reconstruction' } })
}

const activeIcon = computed(() => {
  const active = summary.value.active
  return active ? (active.current_mode === 'search' ? 'search' : 'waypoints') : 'folder'
})
</script>

<template>
  <div v-if="!settings.onboarded && step === 'splash'" class="mm-screen" data-testid="screen-splash" style="padding-bottom:28px;gap:20px">
    <div style="margin-top:28px;font-size:56px;line-height:60px;font-weight:500;letter-spacing:-0.02em">Mind<br>Detective</div>
    <div style="font-size:18px;line-height:26px;color:#587196;max-width:300px">Превращаем фрагменты в проверяемый контекст.</div>
    <div style="flex:1;display:flex;align-items:center;justify-content:center;min-height:240px">
      <SplashParticles />
    </div>
    <div style="height:6px;border-radius:99px;background:linear-gradient(90deg,#4AEEFC,#0B86EA)" />
    <div style="font-size:15px;color:#587196">Готово к работе офлайн</div>
    <MdButton size="lg" block icon-right="arrow-right" data-testid="splash-start" @click="step = 'onb'">Начать</MdButton>
  </div>

  <div v-else-if="!settings.onboarded" class="mm-screen" data-testid="screen-onboarding" style="gap:16px;padding-bottom:28px">
    <div style="margin-top:20px"><img :src="logoMark" alt="" style="width:48px;height:48px"></div>
    <h1 style="margin:8px 0 0;font-size:36px;line-height:42px;font-weight:700;letter-spacing:-0.02em;text-wrap:pretty">Ищите потерянное по шагам, а не по кругу</h1>
    <div style="font-size:16px;line-height:24px;color:#587196;text-wrap:pretty">Зафиксируем, что уже известно и проверено, затем выберем один полезный следующий шаг.</div>
    <MdGlassCard :padding="8">
      <div style="display:grid">
        <div v-for="o in onbItems" :key="o.title" style="display:flex;gap:14px;align-items:flex-start;padding:14px 12px">
          <div class="mm-tile" style="width:40px;height:40px;border-radius:14px;background:#E3F1FF;color:#0B86EA"><MdIcon :name="o.icon" :size="20" /></div>
          <div style="display:grid;gap:3px"><strong style="font-size:16px;line-height:22px;font-weight:650">{{ o.title }}</strong><span style="font-size:14px;line-height:20px;color:#587196">{{ o.body }}</span></div>
        </div>
      </div>
    </MdGlassCard>
    <div style="flex:1" />
    <div class="mm-privacy-line"><MdIcon name="shield-check" :size="16" /><span>Канонические данные дела хранятся на этом устройстве.</span></div>
    <MdButton size="lg" block icon-right="arrow-right" data-testid="onboarding-finish" @click="finishOnboarding">Понятно, начать</MdButton>
  </div>

  <div v-else class="mm-screen" data-testid="screen-home" style="padding-bottom:24px">
    <MdAppHeader :logo-src="logoMark" subtitle="Системный поиск потерянного" show-settings @settings="navigateTo('/settings')" />
    <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px 0 16px;min-height:420px">
      <span class="mm-overline">Новое дело</span>
      <h1 style="margin:8px 0 0;font-size:34px;line-height:40px;font-weight:700;letter-spacing:-0.02em">Что потерялось?</h1>
      <div class="mm-mic-ring">
        <div class="mm-mic-glass">
          <button type="button" class="mm-mic" aria-label="Рассказать голосом, что потерялось" data-testid="home-voice" @click="navigateTo({ path: '/new', query: { voice: '1' } })">
            <MdIcon name="mic" :size="56" color="#fff" :stroke-width="2" />
          </button>
        </div>
      </div>
      <strong style="font-size:17px;line-height:24px;font-weight:650">Нажмите и расскажите, что ищете</strong>
      <span style="margin-top:6px;font-size:15px;line-height:22px;color:#587196;max-width:290px;text-wrap:pretty">Вещь, фото или файл — вспомним, как всё было, и проверим места и источники по шагам.</span>
      <div style="margin-top:14px"><MdButton variant="ghost" size="sm" icon="pencil" data-testid="home-write" @click="navigateTo('/new')">Написать вручную</MdButton></div>
    </div>
    <MdGlassCard :padding="8">
      <div style="display:grid;gap:4px">
        <template v-if="summary.active">
          <MdListRow :icon="activeIcon" :title="summary.active.item_label" :subtitle="summary.activeSub" chevron data-testid="home-active-case" @click="openActive" />
          <div style="height:1px;background:rgba(88,113,150,.14);margin:0 12px" />
        </template>
        <MdListRow icon="folder" title="Все дела" :subtitle="summary.listSub" chevron data-testid="home-all-cases" @click="navigateTo('/cases')" />
      </div>
    </MdGlassCard>
  </div>
</template>
