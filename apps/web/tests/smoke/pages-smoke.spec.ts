import { expect, test, type Page } from '@playwright/test'

// Paths are relative (no leading slash) so they resolve under the Pages sub-path.

function watchFailures(page: Page, origin: string): string[] {
  const failures: string[] = []
  page.on('pageerror', error => failures.push(`pageerror: ${error.message}`))
  page.on('response', (response) => {
    if (response.url().startsWith(origin) && response.status() >= 400) failures.push(`${response.status()} ${response.url()}`)
  })
  return failures
}

async function installServiceWorker(page: Page): Promise<void> {
  await page.goto('./', { waitUntil: 'networkidle' })
  await page.evaluate(async () => { await navigator.serviceWorker.ready })
  // Second load so the page is controlled and the precache is complete.
  await page.reload({ waitUntil: 'networkidle' })
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true)
  await expect(page.locator('.mm-app')).toHaveAttribute('data-routes-ready', 'true')
}

test('published site loads under its base path with the PWA wiring', async ({ page, baseURL }) => {
  const base = new URL(baseURL!)
  const failures = watchFailures(page, base.origin)

  await page.goto('./', { waitUntil: 'networkidle' })
  await expect(page.getByTestId('screen-splash')).toContainText('Превращаем фрагменты в проверяемый контекст.')
  await expect(page.getByTestId('splash-start')).toBeVisible()

  const manifestHref = await page.locator('link[rel="manifest"]').getAttribute('href')
  expect(manifestHref, 'manifest link').toBeTruthy()
  const manifestURL = new URL(manifestHref!, page.url())
  expect(manifestURL.pathname.startsWith(base.pathname)).toBe(true)
  const manifest = await (await page.request.get(manifestURL.href)).json()
  expect(manifest.icons?.length ?? 0).toBeGreaterThan(0)

  const scriptURL = await page.evaluate(async () => (await navigator.serviceWorker.ready).active?.scriptURL ?? '')
  expect(new URL(scriptURL).pathname).toBe(`${base.pathname}sw.js`)

  const notFound = await page.request.get(new URL('404.html', base).href)
  expect(notFound.status()).toBeLessThan(500)

  expect(failures).toEqual([])
})

const ACCOUNT = 'Вышел из офиса, зашёл в кафе. Дома ключей уже не было.'

/** Onboarding → new case → free account → exact-time event, all through in-app navigation. */
async function createCaseInApp(page: Page): Promise<void> {
  await page.getByTestId('splash-start').click()
  await page.getByTestId('onboarding-finish').click()
  await expect(page.getByTestId('screen-home')).toBeVisible()
  await page.getByTestId('home-write').click()
  await page.locator('#new-case-title').fill('Смоук: ключи')
  await page.getByTestId('create-reconstruction').click()
  await expect(page).toHaveURL(/\/cases\/[^/?]+\?tab=/)

  await page.locator('#free-account').fill(ACCOUNT)
  await page.getByTestId('free-account-save').click()
  await expect(page.getByTestId('free-account-save')).toBeDisabled()

  await page.getByTestId('add-event').click()
  await page.locator('#event-title').fill('Вышел из офиса')
  await page.getByRole('radio', { name: 'Точное' }).click()
  await page.getByTestId('event-time').pressSequentially('0830')
  await page.getByTestId('event-submit').click()
  await expect(page.getByTestId('sheet-event')).toHaveCount(0)
}

async function expectCaseRestored(page: Page): Promise<void> {
  await expect(page.getByTestId('screen-case')).toContainText('Вышел из офиса')
  await expect(page.locator('#free-account')).toHaveValue(ACCOUNT)
}

test('installed PWA works offline: onboarding and a case are saved and reopened in-app', async ({ page, context, baseURL }) => {
  const failures = watchFailures(page, new URL(baseURL!).origin)
  await installServiceWorker(page)
  await context.setOffline(true)

  await createCaseInApp(page)
  await page.locator('[data-nav="cases"]').click()
  await expect(page.getByTestId('case-card')).toHaveCount(1)
  await page.getByTestId('case-card').click()
  await expectCaseRestored(page)

  await context.setOffline(false)
  expect(failures).toEqual([])
})

test('installed PWA reopens offline from the service worker cache', async ({ page, context, baseURL, browserName }) => {
  // Playwright's offline emulation in WebKit fails every top-level navigation in the driver,
  // before the service worker can answer, so a full offline reload is verifiable only in Chromium.
  test.skip(browserName === 'webkit', 'WebKit driver cannot emulate an offline top-level navigation')
  const failures = watchFailures(page, new URL(baseURL!).origin)
  await installServiceWorker(page)
  await context.setOffline(true)

  await page.reload()
  await createCaseInApp(page)
  await page.reload()
  await expectCaseRestored(page)

  await context.setOffline(false)
  expect(failures).toEqual([])
})
