<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'
import { exportCase } from '~/lib/storage/exportImport'

const props = withDefaults(defineProps<{
  caseValue: CaseV2
  allowDelete?: boolean
}>(), {
  allowDelete: false,
})
const emit = defineEmits<{ deleted: [] }>()
const repository = useCaseRepository()
const { t } = useCopy()
const confirmingDelete = ref(false)
const deleting = ref(false)

function downloadCase(): void {
  const blob = exportCase(props.caseValue)
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `mind-detective-${props.caseValue.case_id}.json`
  anchor.click()
  URL.revokeObjectURL(url)
}

async function deleteCase(): Promise<void> {
  if (deleting.value) return
  deleting.value = true
  try {
    await repository.delete(props.caseValue.case_id)
    emit('deleted')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <aside class="privacy-note" data-testid="case-data-actions">
    <strong>{{ t('storage.export_title') }}</strong>
    <p>{{ t('storage.export_copy') }}</p>
    <button class="secondary-action" data-testid="export-case" type="button" @click="downloadCase">
      {{ t('storage.export_action') }}
    </button>

    <div v-if="allowDelete" class="case-delete-actions">
      <button
        v-if="!confirmingDelete"
        class="secondary-action"
        data-testid="delete-case"
        type="button"
        @click="confirmingDelete = true"
      >
        {{ t('storage.delete_action') }}
      </button>
      <div v-else data-testid="delete-case-confirmation">
        <strong>{{ t('storage.delete_title') }}</strong>
        <p>{{ t('storage.delete_warning') }}</p>
        <div class="dialog-actions">
          <button class="secondary-action" type="button" :disabled="deleting" @click="confirmingDelete = false">
            {{ t('common.cancel') }}
          </button>
          <button
            class="primary-action"
            data-testid="confirm-delete-case"
            type="button"
            :disabled="deleting"
            @click="deleteCase"
          >
            {{ t('storage.delete_confirm') }}
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>
