<script setup lang="ts">
import type { SourcedProposal } from '~/lib/assistant/proposals'
import type { KindVocabulary } from '~/lib/mobile/vocab'

const props = defineProps<{ proposal: SourcedProposal | null, busy: boolean, words: KindVocabulary, hint: string }>()
const emit = defineEmits<{ ask: [], accept: [], dismiss: [] }>()

const kindLabel = computed(() => (props.proposal?.kind === 'check' ? props.words.check : 'Уточняющий вопрос'))
const sourceLabel = computed(() => (props.proposal?.source === 'assistant' ? 'Ассистент · только исследование' : 'Контрольный список'))
const note = computed(() => props.proposal?.reason === 'rejected'
  ? 'Ответ ассистента не прошёл проверку — показан безопасный шаг из контрольного списка.'
  : props.proposal?.reason === 'unavailable'
    ? 'Ассистент недоступен — использован локальный контрольный список.'
    : '')
const askLabel = computed(() => (props.busy ? 'Думаю…' : props.proposal ? 'Другое предложение' : 'Предложить следующий шаг'))
</script>

<template>
  <MdGlassCard variant="research" data-testid="assistant-card">
    <div style="display:grid;gap:12px">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
        <strong style="font-size:18px;font-weight:650">Ассистент</strong>
        <MdStatusChip status="research" size="sm" />
      </div>
      <span v-if="!proposal" style="font-size:15px;line-height:22px;color:#587196">{{ hint }}</span>
      <div v-else style="display:grid;gap:8px" data-testid="assistant-proposal" :data-source="proposal.source">
        <span style="font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#587196;font-weight:650">{{ kindLabel }} · {{ sourceLabel }}</span>
        <strong style="font-size:18px;line-height:25px;font-weight:650" data-testid="assistant-proposal-text">{{ proposal.text }}</strong>
        <span v-if="note" style="font-size:14px;line-height:20px;color:#587196">{{ note }}</span>
        <span style="font-size:14px;line-height:20px;color:#587196">Предложение не становится фактом автоматически.</span>
        <MdButton block data-testid="assistant-accept" @click="emit('accept')">{{ proposal.kind === 'check' ? 'Добавить в список проверки' : 'Ответить' }}</MdButton>
        <MdButton variant="ghost" block @click="emit('dismiss')">Отклонить</MdButton>
      </div>
      <MdButton variant="secondary" block icon="sparkles" :disabled="busy" data-testid="assistant-ask" @click="emit('ask')">{{ askLabel }}</MdButton>
    </div>
  </MdGlassCard>
</template>
