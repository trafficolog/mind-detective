import { readdirSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { ICONS } from '../../app/lib/ds/icons'
import { STATUS_MAP } from '../../app/lib/ds/statusMap'
import { vocab } from '../../app/lib/mobile/vocab'

const APP = resolve(process.cwd(), 'app')

function files(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry =>
    entry.isDirectory() ? files(join(dir, entry.name)) : [join(dir, entry.name)])
}

const mobileSources = [
  ...files(join(APP, 'components/ds')),
  ...files(join(APP, 'components/mobile')),
  join(APP, 'pages/index.vue'), join(APP, 'pages/new.vue'), join(APP, 'pages/settings.vue'),
  join(APP, 'pages/cases/index.vue'), join(APP, 'pages/cases/[id].vue'),
].filter(file => file.endsWith('.vue'))

describe('Glass Modern design system contract', () => {
  it('every icon referenced by the mobile shell exists in the offline Lucide set', () => {
    const referenced = new Set<string>()
    for (const file of mobileSources) {
      const source = readFileSync(file, 'utf8')
      for (const match of source.matchAll(/(?<![:\w-])(?:icon|name|icon-right)="([a-z0-9-]+)"/g)) referenced.add(match[1]!)
      for (const match of source.matchAll(/'((?:circle|arrow|chevron|map|list|notebook|key|folder|trash|message|flask|file|shield|rotate|package|hard|wifi|triangle|mic)[a-z0-9-]*)'/g)) referenced.add(match[1]!)
    }
    for (const [, icon] of Object.values(STATUS_MAP)) if (icon !== 'dot') referenced.add(icon)
    referenced.add(vocab('physical').icon)
    referenced.add(vocab('digital').icon)
    const notIcons = new Set(['trailing', 'keydown', 'trash'])
    const missing = [...referenced].filter(name => !notIcons.has(name) && !ICONS[name])
    expect(missing).toEqual([])
  })

  it('bundles tokens, fonts and components without remote font or icon hosts', () => {
    const css = files(join(APP, 'assets/css/glass')).map(file => readFileSync(file, 'utf8')).join('\n')
    for (const token of ['--action-primary:#0B86EA', '--text-primary:#0B1733', '--confirmed-bg:#E8F8F1', '--unknown-fg:#B87800', '--contradiction-fg:#D93845', '--research-fg:#7A35D8', '--mode-search-fg:#0A6E80', '--radius-sheet:30px', '--dur-fast:140ms']) {
      expect(css).toContain(token)
    }
    expect(css).not.toContain('fonts.googleapis.com')
    const icon = readFileSync(join(APP, 'components/ds/MdIcon.vue'), 'utf8')
    expect(icon).not.toContain('unpkg.com')
  })

  it('mobile copy never presents probabilities or certainty', () => {
    const forbidden = /вероятн|скорее всего|мы найд|найдём|ИИ уверен|точность \d/i
    for (const file of mobileSources) {
      expect(readFileSync(file, 'utf8'), file).not.toMatch(forbidden)
    }
  })
})
