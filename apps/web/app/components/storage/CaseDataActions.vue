<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'
import { exportCase } from '~/lib/storage/exportImport'

const props = defineProps<{ caseValue: CaseV2 }>()

function downloadCase(): void {
  const blob = exportCase(props.caseValue)
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `mind-detective-${props.caseValue.case_id}.json`
  anchor.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <aside class="privacy-note" data-testid="case-data-actions">
    <strong>Резервная копия дела</strong>
    <p>Экспорт сохраняет полный versioned Case JSON на вашем устройстве. Файл не загружается в облако.</p>
    <button class="secondary-action" data-testid="export-case" type="button" @click="downloadCase">Экспортировать JSON</button>
  </aside>
</template>
