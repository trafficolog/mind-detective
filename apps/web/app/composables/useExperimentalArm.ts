import { computed, type ComputedRef } from 'vue'
import type { ExperimentalArm } from '~/lib/api/contracts'

export function useExperimentalArm(): ComputedRef<ExperimentalArm> {
  const config = useRuntimeConfig()
  const evaluation = useEvaluationSession()
  return computed(() => {
    const activeEvaluation = evaluation.session.value
    if (activeEvaluation) return evaluation.effectiveProductArm(activeEvaluation)
    return config.public.mindDetectiveArm === 'assistant' ? 'assistant' : 'checklist'
  })
}
