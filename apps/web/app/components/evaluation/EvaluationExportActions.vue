<script setup lang="ts">
import { buildEvaluationExport, exportEvalCsv, exportEvalJson } from '~/lib/eval/log'

const pending = ref<'json' | 'csv' | null>(null)
const errorCode = ref<string | null>(null)

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.style.display = 'none'
  document.body.append(anchor)
  anchor.click()
  anchor.remove()
  setTimeout(() => URL.revokeObjectURL(url), 0)
}

async function exportData(format: 'json' | 'csv'): Promise<void> {
  if (pending.value) return
  pending.value = format
  errorCode.value = null
  try {
    const bundle = await buildEvaluationExport()
    const date = new Date().toISOString().slice(0, 10)
    if (format === 'json') {
      downloadBlob(exportEvalJson(bundle), `mind-detective-evaluation-${date}.json`)
    } else {
      downloadBlob(exportEvalCsv(bundle), `mind-detective-evaluation-${date}.csv`)
    }
  } catch (error: unknown) {
    errorCode.value = error instanceof Error ? error.message : 'MD_WEB_EVAL_EXPORT_FAILED'
  } finally {
    pending.value = null
  }
}
</script>

<template>
  <section class="privacy-note" data-testid="evaluation-export-actions">
    <strong>Локальный export evaluation</strong>
    <p>Экспорт содержит только версионированные participant/session/event записи и не читает Case payload.</p>
    <div class="dialog-actions">
      <button
        class="secondary-action"
        data-testid="export-evaluation-json"
        type="button"
        :disabled="pending !== null"
        @click="exportData('json')"
      >
        Экспорт JSON
      </button>
      <button
        class="secondary-action"
        data-testid="export-evaluation-csv"
        type="button"
        :disabled="pending !== null"
        @click="exportData('csv')"
      >
        Экспорт CSV
      </button>
    </div>
    <p v-if="errorCode" role="alert"><code>{{ errorCode }}</code></p>
  </section>
</template>
