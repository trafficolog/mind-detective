<script setup lang="ts">
import type { CaseV2 } from '~/lib/api/contracts'
import type { EvaluationSessionV1 } from '~/lib/eval/contracts'

const config = useRuntimeConfig()
const evaluation = useEvaluationSession()
const activeSession = ref<EvaluationSessionV1 | null>(evaluation.session.value)

function handleStarted(session: EvaluationSessionV1): void {
  activeSession.value = session
}

async function handleCreated(caseValue: CaseV2): Promise<void> {
  await navigateTo(`/cases/${caseValue.case_id}`)
}
</script>

<template>
  <main class="home-screen" data-testid="evaluation-page">
    <section class="hero-panel">
      <p class="eyebrow">MIND Detective · Evaluation</p>
      <h1>Product Evaluation</h1>
      <p class="lede">Evaluation mode включается явно и хранит assignment отдельно от Case.</p>
    </section>

    <section v-if="config.public.mindDetectiveEvaluationEnabled !== true" class="privacy-note" data-testid="evaluation-disabled">
      Evaluation mode выключен в этой сборке.
    </section>

    <template v-else>
      <EvaluationStartPanel @started="handleStarted" />

      <section v-if="activeSession" class="privacy-note" data-testid="evaluation-assignment">
        <strong>Assignment зафиксирован</strong>
        <p data-testid="evaluation-arm">Arm {{ activeSession.arm }}</p>
        <p v-if="activeSession.protocol === 'staged'" data-testid="evaluation-scenario">
          {{ activeSession.scenario_family }} / variant {{ activeSession.scenario_variant }} / position {{ activeSession.order_position }}
        </p>
        <p v-if="activeSession.case_id">Case уже привязан: {{ activeSession.case_id }}</p>
      </section>

      <section v-if="activeSession && !activeSession.case_id" class="hero-panel" data-testid="evaluation-case-create">
        <h2>Создать Case для назначенной session</h2>
        <CreateCaseForm :evaluation-session-id="activeSession.evaluation_session_id" @created="handleCreated" />
      </section>
    </template>
  </main>
</template>
