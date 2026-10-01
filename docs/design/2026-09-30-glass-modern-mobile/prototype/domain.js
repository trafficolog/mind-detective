// Pure domain kernel for the MIND Detective prototype. No DOM, no storage. Immutable updates.
export const SCHEMA = 'mind-detective-proto/v1';
export const METHODS = { visual: 'Осмотрел', hand: 'Проверил руками', flashlight: 'С фонарём', opened: 'Открыл', moved: 'Сдвинул', asked: 'Спросил' };
export const DIGITAL_METHODS = { 'name-search': 'Поиск по названию', 'date-filter': 'Фильтр по дате', browsed: 'Просмотрел папку или альбом', trash: 'Проверил «Удалённые» / корзину', shared: 'Проверил переписку и отправленные', asked: 'Спросил человека' };
export const KINDS = ['physical', 'digital'];
export const kindOf = c => c.kind || 'physical';
export const methodsFor = kind => kind === 'digital' ? DIGITAL_METHODS : METHODS;
export const methodLabel = key => METHODS[key] || DIGITAL_METHODS[key] || key;
const VOCAB = {
  physical: { icon: 'key-round', titleHint: 'Например, ключи от машины', place: 'место', places: 'Места проверки', addPlace: 'Добавить место', addPlaceSub: 'Конкретное место или контейнер, который вы сами хотите проверить', placeHint: 'Например, карман рюкзака', goSearch: 'Перейти к физическому поиску', check: 'Физическая проверка', next: 'Следующая физическая проверка', found: 'Вещь найдена', elsewhere: 'В другом, незапланированном месте', noPlace: 'Есть ли место, которое вы ещё не называли? Добавьте его в список сами.', lastSeen: 'Что вы помните о последнем моменте, когда видели вещь?' },
  digital: { icon: 'image', titleHint: 'Например, фото с дня рождения', place: 'источник', places: 'Источники проверки', addPlace: 'Добавить источник', addPlaceSub: 'Устройство, приложение, папка или альбом, которые вы сами хотите проверить', placeHint: 'Например, телефон → Фото → Недавно удалённые', goSearch: 'Перейти к проверке источников', check: 'Проверка источника', next: 'Следующий источник', found: 'Файл найден', elsewhere: 'В другом, незапланированном источнике', noPlace: 'Есть ли устройство или приложение, которое вы ещё не называли? Добавьте его в список сами.', lastSeen: 'Что вы помните о последнем моменте, когда видели этот файл?' },
};
export const vocab = c => VOCAB[kindOf(c)];
export const STATEMENT_TYPES = { recollection: 'Воспоминание', habit: 'Обычная привычка', observation: 'Наблюдение', hypothesis: 'Гипотеза' };
export const PRECISIONS = { exact: 'Точное', approximate: 'Примерное', unknown: 'Неизвестное' };
export const RESULTS = { 'not-found': 'Не нашёл', incomplete: 'Проверка неполная', found: 'Нашёл' };

const uid = () => Math.random().toString(36).slice(2, 9);
const touch = (c, patch, now = Date.now()) => ({ ...c, ...patch, updated: now });
const need = (ok, code) => { if (!ok) throw new Error(code); };
const open = c => { need(!c.outcome, 'case_closed'); return c; };

export function parseTime(s) {
  const m = /^([01]?\d|2[0-3])[:.]([0-5]\d)$/.exec(String(s || '').trim());
  return m ? +m[1] * 60 + +m[2] : null;
}

export function createCase(list, title, mode = 'reconstruction', now = Date.now(), kind = 'physical') {
  const t = String(title || '').trim();
  need(t, 'title_required');
  need(mode === 'reconstruction' || mode === 'search', 'mode_invalid');
  need(KINDS.includes(kind), 'kind_invalid');
  const num = list.reduce((m, c) => Math.max(m, c.num), 0) + 1;
  return { id: uid(), num, title: t, kind, mode, paused: false, outcome: null, freeAccount: '', statements: [], events: [], zones: [], checks: [], created: now, updated: now };
}

export const setFreeAccount = (c, text) => touch(open(c), { freeAccount: String(text ?? '') });

export function addStatement(c, { type, text, time = '', limitation = '' }) {
  open(c);
  need(type in STATEMENT_TYPES, 'type_invalid');
  need(String(text || '').trim(), 'text_required');
  return touch(c, { statements: [...c.statements, { id: uid(), type, text: text.trim(), time: time.trim(), limitation: limitation.trim() }] });
}

export function addEvent(c, { title, time = '', precision }) {
  open(c);
  need(String(title || '').trim(), 'title_required');
  need(precision in PRECISIONS, 'precision_invalid');
  if (precision !== 'unknown') need(parseTime(time) !== null, 'time_invalid');
  const t = precision === 'unknown' ? '' : String(parseTime(time) / 60 | 0).padStart(2, '0') + ':' + String(parseTime(time) % 60).padStart(2, '0');
  return touch(c, { events: [...c.events, { id: uid(), title: title.trim(), time: t, precision }] });
}

// Unknowns and contradictions are derived from user input only; nothing is guessed or auto-resolved.
export function deriveTimeline(c) {
  const known = c.events.filter(e => e.precision !== 'unknown').map(e => ({ ...e, min: parseTime(e.time) }));
  const unknown = c.events.filter(e => e.precision === 'unknown');
  const byTime = {};
  for (const e of known) if (e.precision === 'exact') (byTime[e.min] ||= []).push(e);
  const clash = new Set();
  const contradictions = [];
  for (const g of Object.values(byTime)) {
    const titles = new Set(g.map(e => e.title.toLowerCase()));
    if (titles.size > 1) { g.forEach(e => clash.add(e.id)); contradictions.push({ time: g[0].time, titles: g.map(e => e.title) }); }
  }
  const items = [
    ...known.sort((a, b) => a.min - b.min).map(e => ({ ...e, status: clash.has(e.id) ? 'contradiction' : 'confirmed' })),
    ...unknown.map(e => ({ ...e, status: 'unknown' })),
  ];
  return { items, unknowns: unknown, contradictions };
}

export const setMode = (c, mode) => { open(c); need(mode === 'reconstruction' || mode === 'search', 'mode_invalid'); return touch(c, { mode }); };
export const togglePause = c => touch(open(c), { paused: !c.paused });

export function addZone(c, name) {
  open(c);
  const n = String(name || '').trim();
  need(n, 'title_required');
  need(!c.zones.some(z => z.name.toLowerCase() === n.toLowerCase()), 'zone_exists');
  return touch(c, { zones: [...c.zones, { id: uid(), name: n }] });
}

export function addCheck(c, { place, method, result, note = '' }, now = Date.now()) {
  open(c);
  need(c.mode === 'search', 'not_in_search');
  const p = String(place || '').trim();
  need(p, 'place_required');
  need(method in methodsFor(kindOf(c)), 'method_invalid');
  need(result in RESULTS, 'result_invalid');
  const repeat = c.checks.some(k => k.place.toLowerCase() === p.toLowerCase());
  let n = c;
  if (!c.zones.some(z => z.name.toLowerCase() === p.toLowerCase())) n = addZone(c, p);
  n = touch(n, { checks: [...n.checks, { id: uid(), place: p, method, result, note: note.trim(), repeat, time: now }] }, now);
  return result === 'found' ? closeCase(n, 'found', 'current', now) : n;
}

export function zoneState(c, z) {
  const ks = c.checks.filter(k => k.place.toLowerCase() === z.name.toLowerCase());
  const last = ks[ks.length - 1];
  if (!last) return { done: false, label: 'Не проверено', count: 0 };
  return { done: last.result !== 'incomplete', label: `${methodLabel(last.method)} · ${RESULTS[last.result].toLowerCase()}`, count: ks.length };
}
export const progress = c => ({ done: c.zones.filter(z => zoneState(c, z).done).length, total: c.zones.length });
export const nextZone = c => c.outcome ? null : c.zones.find(z => !zoneState(c, z).done) || null;

export function closeCase(c, kind, where = 'unknown', now = Date.now()) {
  open(c);
  need(kind === 'found' || kind === 'closed', 'outcome_invalid');
  return touch(c, { outcome: { kind, where: kind === 'found' ? where : null, at: now } }, now);
}

export const caseStatus = c => c.outcome ? c.outcome.kind : c.paused ? 'paused' : c.mode === 'search' ? 'active-search' : 'reconstruction';

export const exportCase = c => JSON.stringify({ schema: SCHEMA, case: c }, null, 2);

export function parseImport(text, list = []) {
  let d;
  try { d = JSON.parse(text); } catch { throw new Error('import_invalid'); }
  const c = d && d.schema === SCHEMA && d.case;
  need(c && typeof c.title === 'string' && c.title.trim() && ['statements', 'events', 'zones', 'checks'].every(k => Array.isArray(c[k])), 'import_invalid');
  const num = list.reduce((m, x) => Math.max(m, x.num), 0) + 1;
  return { ...c, kind: KINDS.includes(c.kind) ? c.kind : 'physical', id: list.some(x => x.id === c.id) ? uid() : c.id, num, outcome: c.outcome || null, paused: !!c.paused };
}

export function demoCase(now = Date.now()) {
  let c = createCase([], 'Ключи от машины', 'reconstruction', now);
  c = setFreeAccount(c, 'Вышел из офиса, зашёл в кафе, потом сел в машину и доехал домой. Дома ключей уже не было.');
  c = addStatement(c, { type: 'recollection', text: 'Ключи были в руке, когда выходил из офиса', time: '08:00' });
  c = addStatement(c, { type: 'habit', text: 'Обычно кладу ключи в карман куртки' });
  c = addEvent(c, { title: 'Офис', time: '08:00', precision: 'exact' });
  c = addEvent(c, { title: 'Кафе', time: '08:40', precision: 'approximate' });
  c = addEvent(c, { title: 'Дорога домой', precision: 'unknown' });
  c = setMode(c, 'search');
  c = addZone(c, 'Карман куртки');
  c = addZone(c, 'Рюкзак, основной отсек');
  c = addZone(c, 'Полка в прихожей');
  c = addCheck(c, { place: 'Карман куртки', method: 'hand', result: 'not-found' }, now - 3600e3);
  return { ...c, updated: now - 3600e3 };
}

// ---- Assistant boundary: research-only proposals, deterministic guard + fallback ----
export const assistantContext = c => ({
  item: c.title, kind: kindOf(c), mode: c.mode,
  confirmed: c.statements.filter(s => s.type !== 'hypothesis').map(s => s.text),
  events: c.events.map(e => ({ title: e.title, time: e.time || null, precision: e.precision })),
  contradictions: deriveTimeline(c).contradictions.map(x => x.time + ': ' + x.titles.join(' / ')),
  zones: c.zones.map(z => ({ name: z.name, state: zoneState(c, z).label })),
});

const FORBIDDEN = /\d+\s*%|вероятн|скорее всего|наверн|уверен|точно (там|в )|мы (знаем|найд)|найд[её]м|местонахожд/i;

export function assistantPrompt(c) {
  const search = c.mode === 'search';
  return 'Ты помощник систематического поиска потерянной вещи. Не угадывай, где вещь. Не называй вероятности. Не утверждай факты за пользователя.\n' +
    (search ? (kindOf(c) === 'digital' ? 'Режим: поиск цифрового файла. Предложи ОДИН конкретный источник (устройство, приложение, папка, альбом), которого нет среди проверенных. Не проси доступ к файлам — проверяет пользователь сам.' : 'Режим: поиск. Предложи ОДНУ конкретную физическую проверку места, которого нет среди проверенных.') : 'Режим: реконструкция. Задай ОДИН уточняющий вопрос о последовательности событий.') +
    '\nВерни только JSON: {"kind":"' + (search ? 'check' : 'question') + '","text":"до 160 символов по-русски"' + (search ? ',"place":"короткое название места"' : '') + '}\nКонтекст: ' + JSON.stringify(assistantContext(c));
}

export function guardProposal(raw, c) {
  let p;
  try { p = JSON.parse(/\{[\s\S]*\}/.exec(String(raw))[0]); } catch { throw new Error('proposal_rejected'); }
  const text = String(p.text || '').trim(), place = String(p.place || '').trim();
  need(p.kind === 'question' || p.kind === 'check', 'proposal_rejected');
  need(text.length >= 5 && text.length <= 200 && !FORBIDDEN.test(text), 'proposal_rejected');
  if (p.kind === 'question') return { kind: 'question', text };
  need(c.mode === 'search' && place.length >= 2 && place.length <= 60 && !FORBIDDEN.test(place), 'proposal_rejected');
  need(!c.zones.some(z => z.name.toLowerCase() === place.toLowerCase() && zoneState(c, z).done), 'proposal_rejected');
  return { kind: 'check', text, place };
}

export function fallbackProposal(c) {
  if (c.mode === 'search') {
    const z = nextZone(c);
    return z ? { kind: 'check', place: z.name, text: 'Проверьте: ' + z.name } : { kind: 'question', text: vocab(c).noPlace };
  }
  const u = deriveTimeline(c).unknowns[0];
  return { kind: 'question', text: u ? 'Что вы помните о событии «' + u.title + '»?' : vocab(c).lastSeen };
}

export async function proposalFlow(c, complete, timeoutMs = 10000) {
  try {
    const raw = await Promise.race([complete(assistantPrompt(c)), new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), timeoutMs))]);
    return { ...guardProposal(raw, c), source: 'assistant' };
  } catch (e) {
    return { ...fallbackProposal(c), source: 'fallback', reason: e.message === 'proposal_rejected' ? 'rejected' : 'unavailable' };
  }
}

// ---- Speech-to-text via external Whisper-compatible endpoint (OpenAI /v1/audio/transcriptions shape) ----
export const STT_DEFAULT_MODEL = 'whisper-1';
export function validateSttConfig(cfg) {
  const url = String(cfg && cfg.url || '').trim();
  let u; try { u = new URL(url); } catch { throw new Error('stt_config_invalid'); }
  need(u.protocol === 'https:' || u.hostname === 'localhost' || u.hostname === '127.0.0.1', 'stt_config_invalid');
  return { url, model: String(cfg.model || '').trim() || STT_DEFAULT_MODEL, key: String(cfg.key || '').trim() };
}
export const sttReady = cfg => { try { validateSttConfig(cfg); return true; } catch { return false; } };
export async function transcribe(cfg, blob, fetchImpl = (...a) => fetch(...a), lang = 'ru') {
  const c = validateSttConfig(cfg);
  need(blob && blob.size > 0, 'stt_empty');
  const fd = new FormData();
  fd.append('file', blob, 'speech.' + (String(blob.type).includes('mp4') ? 'mp4' : 'webm'));
  fd.append('model', c.model); fd.append('language', lang); fd.append('response_format', 'json');
  let res, j;
  try { res = await fetchImpl(c.url, { method: 'POST', headers: c.key ? { Authorization: 'Bearer ' + c.key } : {}, body: fd }); } catch { throw new Error('stt_unavailable'); }
  need(res.ok, 'stt_unavailable');
  try { j = await res.json(); } catch { throw new Error('stt_unavailable'); }
  const text = String(j && j.text || '').trim();
  need(text, 'stt_empty');
  return text;
}

export function demoDigitalCase(now = Date.now()) {
  let c = createCase([{ num: 1 }], 'Фото с дня рождения', 'reconstruction', now, 'digital');
  c = setFreeAccount(c, 'Снимал на телефон в субботу вечером, потом кому-то отправлял в мессенджере. В галерее за субботу не нашёл.');
  c = addStatement(c, { type: 'recollection', text: 'Снимал на свой телефон, не на камеру' });
  c = addStatement(c, { type: 'hypothesis', text: 'Может, удалил, когда чистил галерею' });
  c = addEvent(c, { title: 'Съёмка на телефон', time: '19:30', precision: 'approximate' });
  c = addEvent(c, { title: 'Отправка в мессенджер', precision: 'unknown' });
  c = setMode(c, 'search');
  c = addZone(c, 'Телефон → Фото → Недавно удалённые');
  c = addZone(c, 'Мессенджер → чат с семьёй');
  c = addZone(c, 'Облачный фотоархив');
  c = addCheck(c, { place: 'Телефон → Фото → Недавно удалённые', method: 'trash', result: 'not-found' }, now - 1800e3);
  return { ...c, updated: now - 1800e3 };
}

// ---- Canonical export: proto/v1 → mind-detective-case/v2 (docs/SCHEMA_MAPPING.md) ----
const iso = t => new Date(t || 0).toISOString();
export const CASE_V2_KEYS = ['schema', 'case_id', 'item_label', 'created_at', 'updated_at', 'lifecycle', 'statements', 'timeline', 'search_checks', 'candidates', 'next_action', 'constraints', 'outcome', 'current_mode', 'interaction_journal', 'action_feedback'];
export function toCaseV2(c) {
  const o = c.outcome;
  return {
    schema: 'mind-detective-case/v2',
    case_id: c.id,
    item_label: c.title,
    created_at: iso(c.created),
    updated_at: iso(c.updated),
    lifecycle: o ? (o.kind === 'found' ? 'closed_found' : 'closed_unresolved') : c.paused ? 'paused' : 'active',
    statements: c.statements.map(s => ({ id: s.id, statement_type: s.type, text: s.text, event_time: s.time || null, limitation: s.limitation || null, confirmed_by: 'user' })),
    timeline: c.events.length ? { events: c.events.map(e => ({ id: e.id, title: e.title, time: e.time || null, precision: e.precision })) } : null,
    search_checks: c.checks.map(k => ({ id: k.id, place: k.place, method: k.method, result: k.result, note: k.note || null, repeat: k.repeat, checked_at: iso(k.time) })),
    candidates: c.zones.map(z => ({ id: z.id, label: z.name, source: 'user' })),
    next_action: null,
    constraints: kindOf(c) === 'digital' ? ['item_kind:digital'] : [],
    outcome: o ? { schema: 'mind-detective-outcome/v1', case_id: c.id, status: o.kind === 'found' ? 'found' : 'unresolved', user_reported_found_location: o.where || null, preceding_search_check_id: o.kind === 'found' && c.checks.length ? c.checks[c.checks.length - 1].id : null, possible_cause_statement_id: null, prevention_note: null, retention_decision: null, limitations: [] } : null,
    current_mode: c.mode,
    interaction_journal: c.freeAccount ? [{ id: c.id + '-fa', author: 'user', mode: 'reconstruction', entry_type: 'free_account', text: c.freeAccount, created_at: iso(c.created), statement_ids: [], search_check_ids: [] }] : [],
    action_feedback: [],
  };
}

// ---- n8n server: one base URL, two webhooks; provider keys live in n8n Credentials ----
export function serverEndpoints(cfg) {
  const base = String(cfg && cfg.url || '').trim().replace(/\/+$/, '');
  let u; try { u = new URL(base); } catch { throw new Error('server_config_invalid'); }
  need(u.protocol === 'https:' || u.hostname === 'localhost' || u.hostname === '127.0.0.1', 'server_config_invalid');
  const token = String(cfg.token || '').trim();
  return { propose: base + '/webhook/md-propose', transcribe: base + '/webhook/md-transcribe', token };
}
export const serverReady = cfg => { try { serverEndpoints(cfg); return true; } catch { return false; } };
export const serverStt = cfg => { const e = serverEndpoints(cfg); return { url: e.transcribe, key: e.token }; };
export const serverComplete = (cfg, fetchImpl = (...a) => fetch(...a)) => async prompt => {
  const e = serverEndpoints(cfg);
  const res = await fetchImpl(e.propose, { method: 'POST', headers: { 'Content-Type': 'application/json', ...(e.token ? { Authorization: 'Bearer ' + e.token } : {}) }, body: JSON.stringify({ prompt }) });
  if (!res.ok) throw new Error('server_unavailable');
  const j = await res.json();
  return String(j && j.text || '');
};
