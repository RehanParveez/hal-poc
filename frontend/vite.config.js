import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Hal — Agri-Fintech Platform',
        short_name: 'Hal',
        description: 'Digital escrow and verification platform connecting farmers, banks, and buyers.',
        theme_color: '#15803d',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        runtimeCaching: [
          {
            urlPattern: /\/credit\/checks\/.*\/status\/$/,
            handler: 'NetworkOnly',
          },
          {
            urlPattern: /\/community\/numberdars\/$/,
            handler: 'StaleWhileRevalidate',
            options: { cacheName: 'numberdars-cache', expiration: { maxAgeSeconds: 30 * 60 } },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})