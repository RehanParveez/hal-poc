<template>
  <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
    <div>
      <h2 class="text-sm font-semibold text-gray-700">{{ pageTitle }}</h2>
      <p class="text-xs text-gray-400">{{ auth.user?.district }} · {{ auth.user?.province }}</p>
    </div>
    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium capitalize">
      {{ auth.user?.role }}
    </span>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const PATH_TITLES = {
  '/farmer/dashboard': 'Farmer Dashboard',
  '/landowner/dashboard': 'Landowner Dashboard',
  '/bank/dashboard': 'Loan Approval Queue',
  '/factory/dashboard': 'Factory Dashboard',
  '/shopkeeper/dashboard': 'Shopkeeper Dashboard',
  '/insurance/dashboard': 'Insurance Dashboard',
  '/afo/dashboard': 'AFO Dashboard',
}

const auth = useAuthStore()
const route = useRoute()
const pageTitle = computed(() => PATH_TITLES[route.path] || 'FasalPay')
</script>