export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const evaluation = useEvaluationSession()
  const config = useRuntimeConfig()
  if (config.public.mindDetectiveEvaluationEnabled !== true) {
    evaluation.clear()
    return
  }

  if (to.path.startsWith('/cases/')) {
    const caseId = String(to.params.id || '')
    if (caseId) {
      await evaluation.loadForCase(caseId)
      return
    }
  }

  if (!to.path.startsWith('/evaluation')) evaluation.clear()
})
