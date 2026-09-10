<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'
import { deriveProgress } from '~/lib/case/derived'

const props = defineProps<{ caseValue: CaseV2 }>()
const progress = computed(() => deriveProgress(props.caseValue))
</script>

<template>
  <div class="progress-strip" aria-label="Состояние поиска" data-testid="progress-strip">
    <div class="progress-stat" data-testid="progress-checked"><strong>{{ progress.checked }}</strong><span>Проверено</span></div>
    <div class="progress-stat" data-testid="progress-remaining"><strong>{{ progress.remaining }}</strong><span>Осталось</span></div>
    <div class="progress-stat" data-testid="progress-inaccessible"><strong>{{ progress.inaccessible }}</strong><span>Недоступно</span></div>
  </div>
</template>
