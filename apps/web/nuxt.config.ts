export default defineNuxtConfig({
  ssr: false,
  devtools: { enabled: false },
  modules: ['@vite-pwa/nuxt'],
  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],
  css: [
    '~/assets/css/glass/fonts.css',
    '~/assets/css/glass/colors.css',
    '~/assets/css/glass/typography.css',
    '~/assets/css/glass/spacing.css',
    '~/assets/css/glass/effects.css',
    '~/assets/css/glass/base.css',
    '~/assets/css/glass/components.css',
    '~/assets/css/mobile.css',
    '~/assets/css/tokens.css',
    '~/assets/css/app.css',
  ],
  app: {
    head: {
      htmlAttrs: { lang: 'ru' },
      title: 'Mind Detective',
      meta: [
        { name: 'theme-color', content: '#EEF7FF' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
      ],
      link: [
        { rel: 'manifest', href: '/manifest.webmanifest' },
        { rel: 'icon', href: '/icon.svg', type: 'image/svg+xml' },
        { rel: 'icon', href: '/icon-192.png', type: 'image/png', sizes: '192x192' },
        { rel: 'icon', href: '/icon-512.png', type: 'image/png', sizes: '512x512' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' },
      ],
    },
  },
  runtimeConfig: {
    public: {
      mindDetectiveApiBase: process.env.NUXT_PUBLIC_MIND_DETECTIVE_API_BASE || 'http://127.0.0.1:8000',
      mindDetectiveArm: process.env.NUXT_PUBLIC_MIND_DETECTIVE_ARM || 'checklist',
      mindDetectiveLocale: process.env.NUXT_PUBLIC_MIND_DETECTIVE_LOCALE || 'auto',
      mindDetectiveEvaluationEnabled: process.env.NUXT_PUBLIC_MIND_DETECTIVE_EVALUATION === '1',
    },
  },
  pwa: {
    registerType: 'autoUpdate',
    manifest: false,
    includeAssets: ['icon.svg', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png', 'brand/*', 'fonts/*.woff2'],
    workbox: {
      globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
      globIgnores: ['200.html', '404.html'],
      runtimeCaching: [],
      navigateFallback: '/',
      navigateFallbackDenylist: [/^\/api\//],
      cleanupOutdatedCaches: true,
    },
    devOptions: {
      enabled: false,
    },
  },
  typescript: {
    strict: true,
  },
})
