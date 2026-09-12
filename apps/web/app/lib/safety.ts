export type SafetyRoute = 'ordinary_search' | 'limit_and_escalate'

export interface SafetyDecision {
  route: SafetyRoute
  codes: string[]
  messageKey: 'ordinary_lost_item_search' | 'high_risk_forgotten_action'
}

export class SafetyIngressError extends Error {
  constructor(public readonly code: string) {
    super(code)
    this.name = 'SafetyIngressError'
  }
}

const MEDICATION_PATTERNS = [
  /(?:я\s+)?уже\s+(?:принял|приняла|выпил|выпила)[^\s]*\s+(?:таблет|лекарств|доз)/i,
  /принимал[аи]?\s+ли\s+(?:я\s+)?(?:уже\s+)?(?:таблет|лекарств|доз)/i,
  /\bdid\s+i\s+(?:already\s+)?take\s+(?:the\s+)?(?:pill|medicine|dose)\b/i,
  /\bhave\s+i\s+(?:already\s+)?taken\s+(?:the\s+)?(?:pill|medicine|dose)\b/i,
]

const HAZARDOUS_PATTERNS = [
  /(?:я\s+)?выключил[аи]?\s+(?:плит|утюг|обогревател|газ)/i,
  /(?:я\s+)?перекрыл[аи]?\s+газ/i,
  /\bdid\s+i\s+(?:turn\s+off|shut\s+off)\s+(?:the\s+)?(?:stove|iron|heater|gas)\b/i,
]

const SECURITY_PATTERNS = [
  /(?:я\s+)?(?:запер|заперла|закрыл|закрыла)[^\s]*\s+(?:входн[^\s]*\s+)?двер/i,
  /(?:я\s+)?поставил[аи]?\s+(?:дом|квартир[^\s]*)\s+на\s+сигнализац/i,
  /\bdid\s+i\s+(?:lock|arm)\s+(?:the\s+)?(?:door|alarm)\b/i,
]

function matches(text: string, patterns: RegExp[]): boolean {
  return patterns.some(pattern => pattern.test(text))
}

export function classifySafetyInput(text: string): SafetyDecision {
  const normalized = text.replaceAll('ё', 'е').replaceAll('Ё', 'Е')
  const codes: string[] = []

  if (matches(normalized, MEDICATION_PATTERNS)) codes.push('MD_SAFE_MEDICATION_ACTION')
  if (matches(normalized, HAZARDOUS_PATTERNS)) codes.push('MD_SAFE_HAZARDOUS_ACTION')
  if (matches(normalized, SECURITY_PATTERNS)) codes.push('MD_SAFE_SECURITY_ACTION')

  if (codes.length > 0) {
    return {
      route: 'limit_and_escalate',
      codes: [...new Set(codes)],
      messageKey: 'high_risk_forgotten_action',
    }
  }

  return {
    route: 'ordinary_search',
    codes: [],
    messageKey: 'ordinary_lost_item_search',
  }
}

export function safetyCodeForInput(text: string): string | null {
  const decision = classifySafetyInput(text)
  return decision.route === 'limit_and_escalate' ? decision.codes[0] ?? 'MD_SAFE_HIGH_RISK_ACTION' : null
}

export function enforceSafeInput(text: string): void {
  const code = safetyCodeForInput(text)
  if (code) throw new SafetyIngressError(code)
}
