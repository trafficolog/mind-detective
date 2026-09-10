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
  css: ['~/assets/css/tokens.css', '~/assets/css/app.css'],
  app: {
    head: {
      meta: [
        { name: 'theme-color', content: '#f4f6f8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
      ],
      link: [
        { rel: 'manifest', href: '/manifest.webmanifest' },
        { rel: 'icon', href: '/icon.svg', type: 'image/svg+xml' },
      ],
    },
  },
  runtimeConfig: {
    public: {
      mindDetectiveApiBase: process.env.NUXT_PUBLIC_MIND_DETECTIVE_API_BASE || 'http://127.0.0.1:8000',
      mindDetectiveArm: process.env.NUXT_PUBLIC_MIND_DETECTIVE_ARM || 'checklist',
      mindDetectiveLocale: process.env.NUXT_PUBLIC_MIND_DETECTIVE_LOCALE || 'auto',
    },
  },
  pwa: {
    registerType: 'autoUpdate',
    manifest: false,
    includeAssets: ['icon.svg'],
    workbox: {
      globPatterns: ['**/*.{js,css,html,svg}'],
      runtimeCaching: [],
      navigateFallback: '/index.html',
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
