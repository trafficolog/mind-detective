import { expect, test, type Page } from '@playwright/test'

test.use({ viewport: { width: 430, height: 844 } })

/** Hash of the visible canvas pixels plus the count of painted pixels. */
async function canvasSnapshot(page: Page) {
  return page.getByTestId('splash-particles').evaluate((el) => {
    const canvas = el as HTMLCanvasElement
    const data = canvas.getContext('2d')!.getImageData(0, 0, canvas.width, canvas.height).data
    let painted = 0
    let hash = 0
    for (let i = 0; i < data.length; i += 4) {
      if (data[i + 3]! > 8) painted++
      hash = (hash * 31 + data[i]! + data[i + 1]! * 3 + data[i + 2]! * 7 + data[i + 3]! * 11) >>> 0
    }
    return { painted, hash, total: data.length / 4 }
  })
}

test('splash art is a decorative particle canvas that animates', async ({ page }) => {
  await page.goto('/')
  const art = page.getByTestId('splash-art')
  await expect(art).toHaveAttribute('aria-hidden', 'true')
  await expect(art).toHaveAttribute('data-motion', 'animated')
  await expect(page.getByTestId('splash-particles')).toBeVisible()
  await page.waitForTimeout(400)
  const first = await canvasSnapshot(page)
  expect(first.painted).toBeGreaterThan(first.total * 0.2)
  await page.waitForTimeout(600)
  const second = await canvasSnapshot(page)
  expect(second.hash).not.toBe(first.hash)
  await expect(page.getByTestId('splash-start')).toBeVisible()
})

test('splash art stays still under prefers-reduced-motion', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/')
  const art = page.getByTestId('splash-art')
  await expect(art).toHaveAttribute('data-motion', 'reduced')
  await page.waitForTimeout(200)
  const first = await canvasSnapshot(page)
  expect(first.painted).toBeGreaterThan(first.total * 0.2)
  await page.waitForTimeout(500)
  const second = await canvasSnapshot(page)
  expect(second.hash).toBe(first.hash)
})

test.describe('on a 2x screen', () => {
  test.use({ deviceScaleFactor: 2 })

  test('splash keeps full density on a fast device and lowers it on a slow one', async ({ page, context, browserName }) => {
    test.skip(browserName !== 'chromium', 'CPU throttling is a Chromium DevTools feature')
    // Two page loads in dev mode, one of them on an 8x throttled CPU, need more than the default 30 s.
    test.setTimeout(90_000)
    await page.goto('/')
    const art = page.getByTestId('splash-art')
    // The density only drops after sampling, so wait until sampling has settled before asserting.
    await expect(art).toHaveAttribute('data-render-settled', 'true', { timeout: 15_000 })
    await expect(art).toHaveAttribute('data-render-scale', '2')

    const slow = await context.newPage()
    const cdp = await context.newCDPSession(slow)
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: 8 })
    await slow.goto('/')
    await expect.poll(async () => Number(await slow.getByTestId('splash-art').getAttribute('data-render-scale')), { timeout: 20_000 })
      .toBeLessThanOrEqual(1)
    const painted = await slow.getByTestId('splash-particles').evaluate((el) => {
      const c = el as HTMLCanvasElement
      const d = c.getContext('2d')!.getImageData(0, 0, c.width, c.height).data
      let n = 0
      for (let i = 3; i < d.length; i += 4) if (d[i]! > 8) n++
      return n / (d.length / 4)
    })
    expect(painted).toBeGreaterThan(0.2)
  })
})
