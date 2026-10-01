import type { CaseV2 } from '~/lib/api/contracts'
import { checklistProposal, proposalFlow, type SourcedProposal } from '~/lib/assistant/proposals'
import { serverComplete, serverReady } from '~/lib/assistant/server'

/** Research-only proposal state (ADR 017). Proposals are never persisted into the Case. */
export function useAssistantProposal() {
  const { settings } = useMobileSettings()
  const proposal = useState<SourcedProposal | null>('md-assistant-proposal', () => null)
  const proposalFor = useState<string | null>('md-assistant-proposal-for', () => null)
  const busy = useState<boolean>('md-assistant-busy', () => false)

  const connected = computed(() => serverReady(settings.value.server))

  async function ask(caseValue: CaseV2): Promise<void> {
    busy.value = true
    proposal.value = null
    try {
      const next = settings.value.assistantOn && connected.value
        ? await proposalFlow(caseValue, serverComplete(settings.value.server))
        : checklistProposal(caseValue)
      proposal.value = next
      proposalFor.value = caseValue.case_id
    } finally {
      busy.value = false
    }
  }

  function dismiss(): void {
    proposal.value = null
  }

  function forCase(caseId: string | null | undefined): SourcedProposal | null {
    return proposal.value && proposalFor.value === caseId ? proposal.value : null
  }

  return { proposal, busy, connected, ask, dismiss, forCase }
}
