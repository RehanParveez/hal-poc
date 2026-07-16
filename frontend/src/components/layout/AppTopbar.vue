<template>
  <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
    <div>
      <h2 class="text-sm font-semibold text-gray-700">{{ pageTitle }}</h2>
      <p class="text-xs text-gray-400">{{ auth.user?.district }} · {{ auth.user?.province }}</p>
    </div>
    <div class="flex items-center gap-4">    
    <LanguageSwitcher />           
    <NotificationBell />
    <button v-if="!auth.user?.email" @click="promptForEmail" class="text-xs text-green-700 hover:underline">
    + Add email
  </button>
    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium capitalize">
      {{ auth.user?.role }}
    </span>
   </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import NotificationBell from '@/components/shared/NotificationBell.vue'
import LanguageSwitcher from '@/components/shared/LanguageSwitcher.vue'

const PATH_TITLES = {
  '/farmer/dashboard': 'Farmer Dashboard',
  '/landowner/dashboard': 'Landowner Dashboard',
  '/bank/dashboard': 'Loan Approval Queue',
  '/factory/dashboard': 'Factory Dashboard',
  '/shopkeeper/dashboard': 'Shopkeeper Dashboard',
  '/insurance/dashboard': 'Insurance Dashboard',
  '/afo/dashboard': 'AFO Dashboard',
  '/numberdar/dashboard': 'Numberdar Dashboard',
  '/numberdar/queue': 'Verification Queue',
}

const auth = useAuthStore()
const route = useRoute()
const pageTitle = computed(() => PATH_TITLES[route.path] || 'FasalPay')

async function promptForEmail() {
  const email = window.prompt('Enter your email to receive notifications:')
  if (email && email.trim()) {
    try {
      await auth.updateEmail(email.trim())
    } catch (err) {
      console.error('Failed to update email:', err)
    }
  }
}
</script>