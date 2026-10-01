// Presentation vocabulary for the Glass Modern mobile shell (docs/design/2026-09-30-glass-modern-mobile/MEANING.md).
// Keys are canonical portable-kernel keys; labels are Russian product copy.
export type ItemKind = 'physical' | 'digital'

export const PHYSICAL_METHODS = {
  visual: 'Осмотрел',
  hand: 'Проверил руками',
  flashlight: 'С фонарём',
  opened: 'Открыл',
  moved: 'Сдвинул',
  asked: 'Спросил',
} as const

export const DIGITAL_METHODS = {
  name_search: 'Поиск по названию',
  date_filter: 'Фильтр по дате',
  browsed: 'Просмотрел папку или альбом',
  trash: 'Проверил «Удалённые» / корзину',
  shared: 'Проверил переписку и отправленные',
  asked: 'Спросил человека',
} as const

const LEGACY_METHODS: Record<string, string> = {
  reported_check: 'Отмечено как проверенное',
  glance: 'Быстрый взгляд',
  visual_systematic: 'Осмотрел систематически',
  empty_and_check: 'Опустошил и проверил',
  tactile: 'Проверил на ощупь',
}

export type MethodKey = keyof typeof PHYSICAL_METHODS | keyof typeof DIGITAL_METHODS

export function methodsFor(kind: ItemKind): Record<string, string> {
  return kind === 'digital' ? DIGITAL_METHODS : PHYSICAL_METHODS
}

export function methodLabel(key: string): string {
  return (PHYSICAL_METHODS as Record<string, string>)[key]
    ?? (DIGITAL_METHODS as Record<string, string>)[key]
    ?? LEGACY_METHODS[key]
    ?? key
}

const DS_METHOD_KEYS: Record<string, string> = {
  visual: 'visual', hand: 'hand', flashlight: 'flashlight', opened: 'opened', moved: 'moved', asked: 'asked',
  name_search: 'name-search', date_filter: 'date-filter', browsed: 'browsed', trash: 'trash', shared: 'shared',
  glance: 'visual', visual_systematic: 'visual', empty_and_check: 'opened', tactile: 'hand',
}

/** Kernel method key → MIND Detective DS `SearchCheckCard` method key (DS_CHANGES §1). */
export function dsMethodKey(key: string): string {
  return DS_METHOD_KEYS[key] ?? 'other'
}

export interface KindVocabulary {
  icon: string
  titleHint: string
  place: string
  places: string
  addPlace: string
  addPlaceSub: string
  placeHint: string
  goSearch: string
  check: string
  next: string
  found: string
  elsewhere: string
  noPlace: string
  lastSeen: string
  notInSearch: string
  exists: string
  emptyJournal: string
}

const VOCAB: Record<ItemKind, KindVocabulary> = {
  physical: {
    icon: 'key-round',
    titleHint: 'Например, ключи от машины',
    place: 'место',
    places: 'Места проверки',
    addPlace: 'Добавить место',
    addPlaceSub: 'Конкретное место или контейнер, который вы сами хотите проверить',
    placeHint: 'Например, карман рюкзака',
    goSearch: 'Перейти к физическому поиску',
    check: 'Физическая проверка',
    next: 'Следующая физическая проверка',
    found: 'Вещь найдена',
    elsewhere: 'В другом, незапланированном месте',
    noPlace: 'Есть ли место, которое вы ещё не называли? Добавьте его в список сами.',
    lastSeen: 'Что вы помните о последнем моменте, когда видели вещь?',
    notInSearch: 'Сначала перейдите к физическому поиску.',
    exists: 'Такое место уже есть в списке.',
    emptyJournal: 'Здесь появятся физические проверки с местом и способом.',
  },
  digital: {
    icon: 'image',
    titleHint: 'Например, фото с дня рождения',
    place: 'источник',
    places: 'Источники проверки',
    addPlace: 'Добавить источник',
    addPlaceSub: 'Устройство, приложение, папка или альбом, которые вы сами хотите проверить',
    placeHint: 'Например, телефон → Фото → Недавно удалённые',
    goSearch: 'Перейти к проверке источников',
    check: 'Проверка источника',
    next: 'Следующий источник',
    found: 'Файл найден',
    elsewhere: 'В другом, незапланированном источнике',
    noPlace: 'Есть ли устройство или приложение, которое вы ещё не называли? Добавьте его в список сами.',
    lastSeen: 'Что вы помните о последнем моменте, когда видели этот файл?',
    notInSearch: 'Сначала перейдите к проверке источников.',
    exists: 'Такой источник уже есть в списке.',
    emptyJournal: 'Здесь появятся проверки источников со способом и результатом.',
  },
}

export function vocab(kind: ItemKind): KindVocabulary {
  return VOCAB[kind] ?? VOCAB.physical
}

export const STATEMENT_TYPES = {
  recollection: 'Воспоминание',
  habit: 'Обычная привычка',
  observation: 'Наблюдение',
  hypothesis: 'Гипотеза',
} as const

export type StatementTypeKey = keyof typeof STATEMENT_TYPES

export const PRECISIONS = { exact: 'Точное', approximate: 'Примерное', unknown: 'Неизвестное' } as const
export type PrecisionKey = keyof typeof PRECISIONS

export const RESULTS = { not_found: 'Не нашёл', partial: 'Проверка неполная', found: 'Нашёл' } as const
export type ResultKey = keyof typeof RESULTS

export function resultLabel(key: string): string {
  return (RESULTS as Record<string, string>)[key] ?? (key === 'inaccessible' ? 'Недоступно' : key)
}
