<template>
  <button @click="toggle" class="text-xs font-medium text-gray-500 hover:text-gray-800 border rounded px-2 py-1">
    {{ locale === 'ur' ? 'English' : 'اردو' }}
  </button>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n/index.js'
import { useAuthStore } from '@/stores/auth.js'

const { locale } = useI18n()
const auth = useAuthStore()

async function toggle() {
  const next = locale.value === 'ur' ? 'en' : 'ur'
  setLocale(next)
  if (auth.isLoggedIn) {
    try { await auth.updateProfile({ preferred_language: next }) } catch { /* non-critical — UI already switched */ }
  }
}
</script>