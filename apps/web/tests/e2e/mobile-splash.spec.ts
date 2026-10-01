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
