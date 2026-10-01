<script setup lang="ts">
import { serverReady } from '~/lib/assistant/server'
import { exportCase, importCase } from '~/lib/storage/exportImport'

const store = useMobileCases()
const { settings, update } = useMobileSettings()
const fileInput = ref<HTMLInputElement | null>(null)
const importOk = ref(false)
const error = ref<string | null>(null)
const confirmReset = ref(false)

onMounted(() => { void store.ensureLoaded() })

const current = computed(() => store.cases.value.find(c => c.case_id === store.lastCaseId.value) ?? null)
const exportSub = computed(() => (current.value ? `${current.value.item_label} · JSON` : 'Сначала откройте дело'))
const connected = computed(() => serverReady(settings.value.server))
const serverModeText = computed(() => connected.value
  ? 'Подключено: ассистент и распознавание речи идут через ваш n8n.'
  : settings.value.server.url
    ? 'Адрес не подходит: нужен https или localhost.'
    : 'Не подключено. Укажите адрес своего n8n — ключи моделей останутся на сервере.')

function exportCurrent(): void {
  const c = current.value
  if (!c) return
  const link = document.createElement('a')
  link.href = URL.createObjectURL(exportCase(c))
  link.download = `mind-detective-${store.numbers.value.get(c.case_id) ?? 0}.json`
  link.click()
  setTimeout(() => URL.revokeObjectURL(link.href), 500)
}

async function onFile(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  importOk.value = false
  error.value = null
  try {
    let imported = await importCase(file)
    const existing = store.cases.value.find(c => c.case_id === imported.case_id)
    if (existing && JSON.stringify(existing) !== JSON.stringify(imported)) {
      imported = { ...imported, case_id: globalThis.crypto.randomUUID() }
    }
    await store.put(imported)
    store.lastCaseId.value = imported.case_id
    importOk.value = true
  } catch {
    error.value = 'Не удалось импортировать дело: файл или версия схемы не поддерживается.'
  }
}

function setServer(key: 'url' | 'token', event: Event): void {
  update({ server: { ...settings.value.server, [key]: (event.target as HTMLInputElement).value } })
}

async function resetAll(): Promise<void> {
  await store.removeAll()
  confirmReset.value = false
  await navigateTo('/cases')
}
</script>

<template>
  <div data-testid="screen-settings" style="display:grid;gap:16px;align-content:start;padding-bottom:32px">
    <div><MdIconButton icon="arrow-left" label="Назад" @click="navigateTo('/')" /></div>
    <h1 style="margin:0;font-size:34px;line-height:38px;font-weight:700;letter-spacing:-0.02em">Настройки</h1>
    <MdNotice tone="privacy" title="Дела хранятся на этом устройстве">Облачной копии по умолчанию нет; очистка данных сайта может удалить дела. Для важных дел используйте экспорт.</MdNotice>
    <MdNotice tone="privacy" title="Приложение не открывает ваши файлы">Mind Detective не просматривает галерею, файлы и облака. Источники проверяете вы сами — в деле хранятся только их названия и результаты проверок.</MdNotice>
    <span class="mm-overline mm-overline--muted" style="margin-top:6px">Резервная копия</span>
    <MdGlassCard :padding="8">
      <div style="display:grid;gap:4px">
        <MdListRow icon="download" title="Экспортировать текущее дело" :subtitle="exportSub" chevron data-testid="settings-export" @click="exportCurrent" />
        <div style="height:1px;background:rgba(88,113,150,.14);margin:0 12px" />
        <MdListRow icon="upload" title="Импортировать дело" subtitle="JSON-файл с этого устройства" chevron data-testid="settings-import" @click="fileInput?.click()" />
        <input ref="fileInput" type="file" accept="application/json,.json" data-testid="settings-import-file" style="display:none" @change="onFile">
      </div>
    </MdGlassCard>
    <MdNotice v-if="importOk" tone="info" title="Импорт завершён. Дело сохранено локально." compact data-testid="import-ok" />
    <MdNotice v-if="error" tone="error" :title="error" />
    <span class="mm-overline mm-overline--muted" style="margin-top:6px">Сервер ассистента (n8n)</span>
    <MdGlassCard>
      <div style="display:grid;gap:12px">
        <span style="font-size:15px;line-height:22px;color:#587196" data-testid="server-mode">{{ serverModeText }}</span>
        <label class="md-field"><span class="md-field__label">Адрес n8n</span><input class="md-textarea" data-testid="server-url" type="url" autocomplete="off" placeholder="https://n8n.example.com" :value="settings.server.url" @input="setServer('url', $event)"></label>
        <label class="md-field"><span class="md-field__label">Токен доступа к webhook</span><input class="md-textarea" data-testid="server-token" type="password" autocomplete="off" placeholder="Header Auth из n8n" :value="settings.server.token" @input="setServer('token', $event)"></label>
      </div>
    </MdGlassCard>
    <MdNotice tone="privacy" title="Куда уходят данные">На ваш сервер n8n уходит только запрос ассистента с минимальным контекстом (без свободного рассказа и гипотез) и запись голоса. Ключи моделей и распознавания хранятся в n8n, не в браузере. Без адреса ассистент использует локальный контрольный список, а речь распознаёт браузер.</MdNotice>
    <span class="mm-overline mm-overline--muted" style="margin-top:6px">Онлайн-ассистент</span>
    <MdNotice tone="research" title="Только исследование">Ассистент предлагает один следующий шаг и не становится источником фактов. Ответ проходит проверку в приложении; если сервер недоступен или ответ не прошёл проверку, используется локальный контрольный список.</MdNotice>
    <MdButton :variant="settings.assistantOn ? 'secondary' : 'primary'" block icon="sparkles" data-testid="assistant-toggle" @click="update({ assistantOn: !settings.assistantOn })">{{ settings.assistantOn ? 'Отключить онлайн-ассистента' : 'Включить онлайн-ассистента' }}</MdButton>
    <span class="mm-overline mm-overline--muted" style="margin-top:6px">Данные</span>
    <MdButton variant="danger" block data-testid="reset-all" @click="confirmReset = true">Удалить все локальные дела</MdButton>
    <MobileConfirmSheet v-if="confirmReset" title="Удалить все локальные дела?" @close="confirmReset = false" @confirm="resetAll" />
  </div>
</template>
