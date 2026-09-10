export default defineNuxtConfig({
  ssr: false,
  devtools: { enabled: false },
  runtimeConfig: {
    public: {
      mindDetectiveApiBase: process.env.NUXT_PUBLIC_MIND_DETECTIVE_API_BASE || 'http://127.0.0.1:8000',
      mindDetectiveArm: process.env.NUXT_PUBLIC_MIND_DETECTIVE_ARM || 'checklist',
    },
  },
  typescript: {
    strict: true,
  },
})
