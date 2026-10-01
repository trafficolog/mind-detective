<script setup lang="ts">
// Animated splash illustration: a glass sphere assembled from volumetric particles with
// yellow and violet fragment cores over soft sky clouds. Decorative only (aria-hidden),
// offline (no external assets), pauses in background tabs and stays still under
// prefers-reduced-motion. Falls back to the static splash-sphere.png without canvas.
import splashSphere from '~/assets/brand/splash-sphere.png'
import {
  createSplashScene,
  frameAt,
  SPLASH_PALETTE,
  type SplashFrame,
  type SplashGroup,
  type SplashTone,
} from '~/lib/mobile/splashParticles'

const host = ref<HTMLDivElement | null>(null)
const canvas = ref<HTMLCanvasElement | null>(null)
const fallback = ref(false)
const motion = ref<'animated' | 'reduced'>('animated')

const SPRITE_PX = 96
const scene = createSplashScene(20260930)
const CLOUDS = [
  { x: 0.18, y: 0.3, r: 0.34, a: 0.75, speed: 0.000012 },
  { x: 0.82, y: 0.22, r: 0.3, a: 0.6, speed: -0.00001 },
  { x: 0.12, y: 0.78, r: 0.38, a: 0.8, speed: 0.000008 },
  { x: 0.88, y: 0.72, r: 0.32, a: 0.65, speed: -0.000014 },
  { x: 0.5, y: 0.92, r: 0.42, a: 0.7, speed: 0.000006 },
]

const rgba = (tone: SplashTone, a: number) => {
  const [r, g, b] = SPLASH_PALETTE[tone]
  return `rgba(${r},${g},${b},${a})`
}

function makeSprite(tone: SplashTone, group: SplashGroup): HTMLCanvasElement {
  const c = document.createElement('canvas')
  c.width = c.height = SPRITE_PX
  const g = c.getContext('2d')!
  const h = SPRITE_PX / 2
  if (group === 'shell') {
    // Glass bead: clear core, tinted rim, bright specular dot.
    const body = g.createRadialGradient(h * 0.8, h * 0.75, h * 0.05, h, h, h * 0.92)
    body.addColorStop(0, 'rgba(255,255,255,0.35)')
    body.addColorStop(0.5, rgba(tone, 0.18))
    body.addColorStop(0.86, rgba(tone, 0.6))
    body.addColorStop(1, rgba(tone, 0))
    g.fillStyle = body
    g.beginPath(); g.arc(h, h, h * 0.92, 0, Math.PI * 2); g.fill()
  }
  else if (group === 'dust') {
    const glow = g.createRadialGradient(h, h, 0, h, h, h)
    glow.addColorStop(0, 'rgba(255,255,255,0.95)')
    glow.addColorStop(0.35, rgba(tone, 0.6))
    glow.addColorStop(1, rgba(tone, 0))
    g.fillStyle = glow
    g.fillRect(0, 0, SPRITE_PX, SPRITE_PX)
    return c
  }
  else {
    // Fragment orb: soft volumetric droplet; overlapping halos melt neighbours into one fragment.
    const body = g.createRadialGradient(h * 0.8, h * 0.74, h * 0.02, h, h, h)
    body.addColorStop(0, 'rgba(255,255,255,0.75)')
    body.addColorStop(0.22, rgba(tone, 0.85))
    body.addColorStop(0.6, rgba(tone, 0.45))
    body.addColorStop(1, rgba(tone, 0))
    g.fillStyle = body
    g.fillRect(0, 0, SPRITE_PX, SPRITE_PX)
    return c
  }
  const spec = g.createRadialGradient(h * 0.68, h * 0.62, 0, h * 0.68, h * 0.62, h * 0.22)
  spec.addColorStop(0, 'rgba(255,255,255,0.95)')
  spec.addColorStop(1, 'rgba(255,255,255,0)')
  g.fillStyle = spec
  g.fillRect(0, 0, SPRITE_PX, SPRITE_PX)
  return c
}

let sprites = new Map<string, HTMLCanvasElement>()
let ctx: CanvasRenderingContext2D | null = null
let size = { width: 0, height: 0, dpr: 1 }
let raf = 0
let start = 0
let reduced = false
let observer: ResizeObserver | null = null
let media: MediaQueryList | null = null

function spriteFor(tone: SplashTone, group: SplashGroup) {
  const style = group === 'warm' || group === 'cool' ? 'orb' : group
  const key = `${style}:${tone}`
  let s = sprites.get(key)
  if (!s) {
    s = makeSprite(tone, group)
    sprites.set(key, s)
  }
  return s
}

function drawBackdrop(g: CanvasRenderingContext2D, t: number) {
  const { width: w, height: hgt } = size
  const m = Math.min(w, hgt)
  const sky = g.createRadialGradient(w / 2, hgt * 0.55, 0, w / 2, hgt * 0.55, Math.max(w, hgt) * 0.6)
  sky.addColorStop(0, rgba('sky', 0.5))
  sky.addColorStop(1, rgba('sky', 0.12))
  g.fillStyle = sky
  g.fillRect(0, 0, w, hgt)
  for (const cloud of CLOUDS) {
    const cx = ((cloud.x + t * cloud.speed) % 1.2 + 1.2) % 1.2 * w - 0.1 * w
    const cy = cloud.y * hgt
    const r = cloud.r * m
    const grad = g.createRadialGradient(cx, cy, 0, cx, cy, r)
    grad.addColorStop(0, `rgba(255,255,255,${cloud.a})`)
    grad.addColorStop(0.55, `rgba(226,240,255,${cloud.a * 0.45})`)
    grad.addColorStop(1, 'rgba(206,230,255,0)')
    g.fillStyle = grad
    g.fillRect(0, 0, w, hgt)
  }
}

function drawGlassBody(g: CanvasRenderingContext2D, frame: SplashFrame) {
  const { x, y } = frame.center
  const r = frame.radius * frame.progress
  if (r < 1) return
  // Reflection on the "floor" under the sphere.
  g.save()
  g.translate(x, y + frame.radius * 1.12)
  g.scale(1, 0.22)
  const floor = g.createRadialGradient(0, 0, 0, 0, 0, frame.radius * 1.1)
  floor.addColorStop(0, rgba('blue', 0.32 * frame.progress))
  floor.addColorStop(0.5, rgba('sky', 0.18 * frame.progress))
  floor.addColorStop(1, rgba('sky', 0))
  g.fillStyle = floor
  g.beginPath(); g.arc(0, 0, frame.radius * 1.1, 0, Math.PI * 2); g.fill()
  g.restore()

  const body = g.createRadialGradient(x - r * 0.3, y - r * 0.35, r * 0.1, x, y, r)
  body.addColorStop(0, 'rgba(255,255,255,0.5)')
  body.addColorStop(0.62, 'rgba(236,248,255,0.22)')
  body.addColorStop(0.92, rgba('blue', 0.28))
  body.addColorStop(1, rgba('sky', 0))
  g.fillStyle = body
  g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill()
}

function drawGlassHighlights(g: CanvasRenderingContext2D, frame: SplashFrame) {
  const { x, y } = frame.center
  const r = frame.radius * 1.02
  const a = frame.progress
  g.save()
  g.lineCap = 'round'
  g.strokeStyle = `rgba(255,255,255,${0.75 * a})`
  g.lineWidth = Math.max(1.5, r * 0.035)
  g.beginPath(); g.arc(x, y, r * 0.86, Math.PI * 1.08, Math.PI * 1.42); g.stroke()
  g.strokeStyle = `rgba(255,255,255,${0.45 * a})`
  g.lineWidth = Math.max(1, r * 0.018)
  g.beginPath(); g.arc(x, y, r * 0.9, Math.PI * 0.12, Math.PI * 0.38); g.stroke()
  g.strokeStyle = rgba('glass', 0.5 * a)
  g.lineWidth = 1
  g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.stroke()
  g.restore()
}

function draw(now: number) {
  if (!ctx || !size.width) return
  const t = now - start
  const g = ctx
  g.setTransform(size.dpr, 0, 0, size.dpr, 0, 0)
  g.clearRect(0, 0, size.width, size.height)
  const frame = frameAt(scene, t, size, { reducedMotion: reduced })
  drawBackdrop(g, reduced ? 0 : t)
  drawGlassBody(g, frame)
  for (const s of frame.sprites) {
    if (s.alpha <= 0.01 || s.size <= 0.2) continue
    g.globalAlpha = Math.min(1, s.alpha)
    const d = s.size * 2
    g.drawImage(spriteFor(s.tone, s.group), s.x - s.size, s.y - s.size, d, d)
  }
  g.globalAlpha = 1
  drawGlassHighlights(g, frame)
}

function loop(now: number) {
  draw(now)
  raf = reduced || document.hidden ? 0 : requestAnimationFrame(loop)
}

function kick() {
  if (raf) cancelAnimationFrame(raf)
  raf = 0
  if (reduced) draw(performance.now())
  else if (!document.hidden) raf = requestAnimationFrame(loop)
}

function resize() {
  const el = canvas.value
  if (!el || !host.value) return
  const rect = host.value.getBoundingClientRect()
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  size = { width: rect.width, height: rect.height, dpr }
  el.width = Math.max(1, Math.round(rect.width * dpr))
  el.height = Math.max(1, Math.round(rect.height * dpr))
  draw(performance.now())
}

function onMotionChange() {
  reduced = Boolean(media?.matches)
  motion.value = reduced ? 'reduced' : 'animated'
  kick()
}

function onVisibility() {
  kick()
}

onMounted(() => {
  ctx = canvas.value?.getContext('2d') ?? null
  if (!ctx) {
    fallback.value = true
    return
  }
  media = window.matchMedia?.('(prefers-reduced-motion: reduce)') ?? null
  reduced = Boolean(media?.matches)
  motion.value = reduced ? 'reduced' : 'animated'
  media?.addEventListener?.('change', onMotionChange)
  document.addEventListener('visibilitychange', onVisibility)
  start = performance.now()
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(resize)
    observer.observe(host.value!)
  }
  resize()
  kick()
})

onBeforeUnmount(() => {
  if (raf) cancelAnimationFrame(raf)
  observer?.disconnect()
  media?.removeEventListener?.('change', onMotionChange)
  document.removeEventListener('visibilitychange', onVisibility)
  sprites = new Map()
  ctx = null
})
</script>

<template>
  <div ref="host" class="mm-splash-art" data-testid="splash-art" :data-motion="motion" aria-hidden="true">
    <img v-if="fallback" :src="splashSphere" alt="" class="mm-splash-art__fallback">
    <canvas v-else ref="canvas" class="mm-splash-art__canvas" data-testid="splash-particles" />
  </div>
</template>
