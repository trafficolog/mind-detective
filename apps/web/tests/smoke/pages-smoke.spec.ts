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

async function installServiceWorker(page: Page): Promise<string> {
  await page.goto('./', { waitUntil: 'networkidle' })
  const scriptURL = await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready
    return registration.active?.scriptURL ?? ''
  })
  // Second load so the page is controlled and the precache is complete.
  await page.reload({ waitUntil: 'networkidle' })
  return scriptURL
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

test('installed PWA keeps working offline: onboarding, case, account and event survive reload', async ({ page, context, baseURL }) => {
  const failures = watchFailures(page, new URL(baseURL!).origin)
  await installServiceWorker(page)
  await context.setOffline(true)

  await page.reload()
  await page.getByTestId('splash-start').click()
  await page.getByTestId('onboarding-finish').click()
  await expect(page.getByTestId('screen-home')).toBeVisible()

  await page.getByTestId('home-write').click()
  await page.locator('#new-case-title').fill('Смоук: ключи')
  await page.getByTestId('create-reconstruction').click()
  await expect(page).toHaveURL(/\/cases\/[^/?]+\?tab=/)

  const account = 'Вышел из офиса, зашёл в кафе. Дома ключей уже не было.'
  await page.locator('#free-account').fill(account)
  await page.getByTestId('free-account-save').click()
  await expect(page.getByTestId('free-account-save')).toBeDisabled()

  await page.getByTestId('add-event').click()
  await page.locator('#event-title').fill('Вышел из офиса')
  await page.getByRole('radio', { name: 'Точное' }).click()
  await page.getByTestId('event-time').pressSequentially('0830')
  await page.getByTestId('event-submit').click()
  await expect(page.getByTestId('sheet-event')).toHaveCount(0)

  await page.reload()
  await expect(page.getByTestId('screen-case')).toContainText('Вышел из офиса')
  await expect(page.locator('#free-account')).toHaveValue(account)

  await context.setOffline(false)
  expect(failures).toEqual([])
})
