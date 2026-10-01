// Pure model for the animated splash illustration: a glass sphere assembled from
// volumetric particles with yellow and violet fragment cores (the splash-sphere.png motif).
// Deterministic (seeded), framework-free and testable; the canvas component only draws sprites.

export const ASSEMBLE_MS = 2200
const ROTATION_PER_MS = 0.00018
const TILT = 0.38
const FOCAL = 5

export const SPLASH_PALETTE = {
  glass: [236, 248, 255],
  sky: [150, 206, 250],
  cyan: [74, 238, 252],
  blue: [11, 134, 234],
  yellow: [255, 222, 120],
  amber: [255, 196, 92],
  violet: [168, 140, 250],
  indigo: [112, 112, 240],
} as const satisfies Record<string, readonly [number, number, number]>

export type SplashTone = keyof typeof SPLASH_PALETTE
export type SplashGroup = 'shell' | 'warm' | 'cool' | 'dust'
type Vec3 = [number, number, number]

export interface SplashParticle {
  group: SplashGroup
  tone: SplashTone
  home: Vec3
  scatter: Vec3
  delay: number
  size: number
  alpha: number
  phase: number
}

export interface SplashScene {
  seed: number
  particles: SplashParticle[]
}

export interface SplashSprite {
  group: SplashGroup
  tone: SplashTone
  x: number
  y: number
  z: number
  size: number
  alpha: number
}

export interface SplashFrame {
  sprites: SplashSprite[]
  center: { x: number, y: number }
  radius: number
  progress: number
}

function mulberry32(seed: number): () => number {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6D2B79F5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function unitVector(rand: () => number): Vec3 {
  const z = rand() * 2 - 1
  const a = rand() * Math.PI * 2
  const s = Math.sqrt(1 - z * z)
  return [s * Math.cos(a), s * Math.sin(a), z]
}

function scatterFor(home: Vec3, rand: () => number, reach: number): Vec3 {
  const dir = unitVector(rand)
  const k = reach * (0.6 + rand() * 0.6)
  return [home[0] + dir[0] * k, home[1] + dir[1] * k, home[2] + dir[2] * k]
}

/** A blob of particles inside the sphere, clamped to stay within `limit` of the centre. */
function core(rand: () => number, centre: Vec3, spread: Vec3, count: number, limit: number): Vec3[] {
  const out: Vec3[] = []
  while (out.length < count) {
    const d = unitVector(rand)
    const r = Math.cbrt(rand())
    const p: Vec3 = [centre[0] + d[0] * spread[0] * r, centre[1] + d[1] * spread[1] * r, centre[2] + d[2] * spread[2] * r]
    if (Math.hypot(...p) < limit) out.push(p)
  }
  return out
}

export function createSplashScene(seed = 1, shellCount = 240): SplashScene {
  const rand = mulberry32(seed)
  const particles: SplashParticle[] = []
  const golden = Math.PI * (3 - Math.sqrt(5))
  const offset = rand() * Math.PI * 2

  for (let i = 0; i < shellCount; i++) {
    const y = 1 - (2 * (i + 0.5)) / shellCount
    const r = Math.sqrt(1 - y * y)
    const a = i * golden + offset
    const home: Vec3 = [Math.cos(a) * r, y, Math.sin(a) * r]
    const pick = rand()
    particles.push({
      group: 'shell',
      tone: pick < 0.62 ? 'glass' : pick < 0.94 ? 'sky' : 'cyan',
      home,
      scatter: scatterFor(home, rand, 1.4),
      delay: rand() * 0.35,
      size: 0.042 * (0.92 + rand() * 0.16),
      alpha: 0.85,
      phase: rand() * Math.PI * 2,
    })
  }

  for (const home of core(rand, [-0.34, 0.2, 0.12], [0.4, 0.5, 0.34], 42, 0.84)) {
    particles.push({
      group: 'warm',
      tone: rand() < 0.65 ? 'yellow' : 'amber',
      home,
      scatter: scatterFor(home, rand, 1.8),
      delay: 0.15 + rand() * 0.35,
      size: 0.12 + rand() * 0.09,
      alpha: 0.62,
      phase: rand() * Math.PI * 2,
    })
  }

  for (const home of core(rand, [0.22, -0.02, 0.05], [0.46, 0.52, 0.42], 60, 0.84)) {
    particles.push({
      group: 'cool',
      tone: rand() < 0.6 ? 'violet' : 'indigo',
      home,
      scatter: scatterFor(home, rand, 1.8),
      delay: 0.1 + rand() * 0.35,
      size: 0.13 + rand() * 0.1,
      alpha: 0.62,
      phase: rand() * Math.PI * 2,
    })
  }

  for (let i = 0; i < 36; i++) {
    const d = unitVector(rand)
    const r = 1.08 + rand() * 0.07
    const home: Vec3 = [d[0] * r, d[1] * r, d[2] * r]
    particles.push({
      group: 'dust',
      tone: rand() < 0.7 ? 'glass' : 'sky',
      home,
      scatter: scatterFor(home, rand, 0.8),
      delay: rand() * 0.5,
      size: 0.018 + rand() * 0.02,
      alpha: 0.75,
      phase: rand() * Math.PI * 2,
    })
  }

  return { seed, particles }
}

const easeOutCubic = (t: number) => 1 - (1 - t) ** 3
const clamp01 = (t: number) => Math.min(1, Math.max(0, t))

function rotate(p: Vec3, yaw: number, pitch: number): Vec3 {
  const cy = Math.cos(yaw)
  const sy = Math.sin(yaw)
  const x1 = p[0] * cy + p[2] * sy
  const z1 = -p[0] * sy + p[2] * cy
  const cp = Math.cos(pitch)
  const sp = Math.sin(pitch)
  return [x1, p[1] * cp - z1 * sp, p[1] * sp + z1 * cp]
}

/**
 * Projects the scene at time `t` (ms since mount). Reduced motion shows the assembled,
 * resting pose (identical to t = ASSEMBLE_MS) so no movement is ever required.
 */
export function frameAt(
  scene: SplashScene,
  t: number,
  view: { width: number, height: number },
  options: { reducedMotion?: boolean } = {},
): SplashFrame {
  const time = options.reducedMotion ? ASSEMBLE_MS : Math.max(0, t)
  const base = Math.min(view.width, view.height)
  const radius = base * 0.4
  const center = { x: view.width / 2, y: view.height / 2 }
  const yaw = (time - ASSEMBLE_MS) * ROTATION_PER_MS
  const settled = time - ASSEMBLE_MS
  const sprites: SplashSprite[] = []
  let progressSum = 0

  for (const p of scene.particles) {
    const local = clamp01((time / ASSEMBLE_MS - p.delay) / (1 - p.delay))
    const k = easeOutCubic(local)
    progressSum += k
    let pos: Vec3 = [
      p.scatter[0] + (p.home[0] - p.scatter[0]) * k,
      p.scatter[1] + (p.home[1] - p.scatter[1]) * k,
      p.scatter[2] + (p.home[2] - p.scatter[2]) * k,
    ]
    if (p.group === 'warm' || p.group === 'cool') {
      // Fragments drift gently inside the glass, against the shell's rotation.
      const sway = 0.035 * Math.sin(settled * 0.0011 + p.phase)
      pos = rotate([pos[0] + sway, pos[1] + sway * 0.6, pos[2]], -yaw * 1.6, 0)
    }
    else if (p.group === 'dust') {
      const bob = 0.03 * Math.sin(settled * 0.0009 + p.phase)
      pos = [pos[0], pos[1] + bob, pos[2]]
    }
    const [x, y, z] = rotate(pos, yaw, TILT)
    const persp = FOCAL / (FOCAL - z)
    const depth = clamp01((z + 1.2) / 2.4)
    sprites.push({
      group: p.group,
      tone: p.tone,
      x: center.x + x * radius * persp,
      y: center.y + y * radius * persp,
      z,
      size: p.size * radius * persp,
      alpha: p.alpha * (0.3 + 0.7 * depth) * clamp01(local * 1.6),
    })
  }

  sprites.sort((a, b) => a.z - b.z)
  return { sprites, center, radius, progress: progressSum / scene.particles.length }
}
