import { computed, type ComputedRef } from 'vue'
import type { ExperimentalArm } from '~/lib/api/contracts'

export function useExperimentalArm(): ComputedRef<ExperimentalArm> {
  const config = useRuntimeConfig()
  return computed(() => config.public.mindDetectiveArm === 'assistant' ? 'assistant' : 'checklist')
}
