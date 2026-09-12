import type {
  CaseV2,
  JournalEntryV2,
  RebuildTimelinePayload,
  RecordFreeAccountPayload,
  TimelineEventV2,
} from '~/lib/api/contracts'

function freeAccountEntry(caseValue: CaseV2): JournalEntryV2 | undefined {
  return caseValue.interaction_journal.find(entry => (
    entry.author === 'user'
    && entry.mode === 'reconstruction'
    && entry.entry_type === 'free_account'
  ))
}

export function hasFreeAccount(caseValue: CaseV2): boolean {
  return freeAccountEntry(caseValue) !== undefined
}

export function freeAccountText(caseValue: CaseV2): string | null {
  return freeAccountEntry(caseValue)?.text ?? null
}

export function buildRecordFreeAccountPayload(
  entryId: string,
  text: string,
): RecordFreeAccountPayload {
  return {
    entry_id: entryId,
    text,
  }
}

export function buildRebuildTimelinePayload(
  events: TimelineEventV2[],
  lastSupportedInteractionId: string | null,
  firstNoticedMissingId: string | null,
): RebuildTimelinePayload {
  return {
    events,
    last_supported_interaction_id: lastSupportedInteractionId,
    first_noticed_missing_id: firstNoticedMissingId,
  }
}
