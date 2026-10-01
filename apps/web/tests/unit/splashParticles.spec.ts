import { describe, expect, it } from 'vitest'
import {
  ASSEMBLE_MS,
  createSplashScene,
  frameAt,
  SPLASH_PALETTE,
} from '../../app/lib/mobile/splashParticles'

describe('splash particle scene', () => {
  it('is deterministic for the same seed and differs for another seed', () => {
    const a = createSplashScene(7)
    const b = createSplashScene(7)
    const c = createSplashScene(8)
    expect(a).toEqual(b)
    expect(a.particles.map(p => p.home)).not.toEqual(c.particles.map(p => p.home))
  })

  it('builds a glass shell plus yellow and violet fragment cores from the brand palette', () => {
    const scene = createSplashScene(1)
    const groups = new Set(scene.particles.map(p => p.group))
    expect(groups).toEqual(new Set(['shell', 'warm', 'cool', 'dust']))
    for (const particle of scene.particles) {
      expect(Object.keys(SPLASH_PALETTE)).toContain(particle.tone)
      const r = Math.hypot(...particle.home)
      if (particle.group === 'shell') expect(r).toBeCloseTo(1, 5)
      if (particle.group === 'warm' || particle.group === 'cool') expect(r).toBeLessThan(0.95)
    }
    expect(scene.particles.filter(p => p.group === 'warm').every(p => p.tone === 'yellow' || p.tone === 'amber')).toBe(true)
    expect(scene.particles.filter(p => p.group === 'cool').every(p => p.tone === 'violet' || p.tone === 'indigo')).toBe(true)
  })

  it('stays within a small mobile budget', () => {
    const scene = createSplashScene(1)
    expect(scene.particles.length).toBeGreaterThan(150)
    expect(scene.particles.length).toBeLessThanOrEqual(420)
  })

  it('fragments start scattered and assemble into the sphere', () => {
    const scene = createSplashScene(3)
    const start = frameAt(scene, 0, { width: 300, height: 300 })
    const done = frameAt(scene, ASSEMBLE_MS + 10, { width: 300, height: 300 })
    const spread = (f: typeof start) => Math.max(...f.sprites.filter(s => s.group === 'shell').map(s => Math.hypot(s.x - 150, s.y - 150)))
    expect(spread(start)).toBeGreaterThan(spread(done))
    // Assembled shell fits the canvas.
    for (const s of done.sprites) {
      expect(s.x - s.size).toBeGreaterThan(-1)
      expect(s.x + s.size).toBeLessThan(301)
      expect(s.y - s.size).toBeGreaterThan(-1)
      expect(s.y + s.size).toBeLessThan(301)
    }
  })

  it('sorts sprites back-to-front and makes nearer particles larger and more opaque', () => {
    const frame = frameAt(createSplashScene(5), ASSEMBLE_MS + 500, { width: 320, height: 300 })
    for (let i = 1; i < frame.sprites.length; i++) {
      expect(frame.sprites[i]!.z).toBeGreaterThanOrEqual(frame.sprites[i - 1]!.z)
    }
    const shell = frame.sprites.filter(s => s.group === 'shell')
    const back = shell[0]!
    const front = shell[shell.length - 1]!
    expect(front.size).toBeGreaterThan(back.size)
    expect(front.alpha).toBeGreaterThan(back.alpha)
  })

  it('a reduced-motion frame is the assembled resting pose', () => {
    const scene = createSplashScene(9)
    const still = frameAt(scene, 0, { width: 300, height: 300 }, { reducedMotion: true })
    const settled = frameAt(scene, ASSEMBLE_MS, { width: 300, height: 300 })
    expect(still.sprites.map(s => [s.x, s.y])).toEqual(settled.sprites.map(s => [s.x, s.y]))
  })
})
