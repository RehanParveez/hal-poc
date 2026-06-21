<template>
  <aside class="w-64 bg-green-800 text-white flex flex-col shadow-lg">
    <div class="p-5 border-b border-green-700">
      <h1 class="text-xl font-bold">🌾 FasalPay</h1>
      <p class="text-xs text-green-200 mt-1">Pakistan</p>
    </div>

    <nav class="flex-1 py-4 px-3 space-y-1">
      <template v-for="item in navItems" :key="item.path || item.anchor">
        <router-link
          v-if="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors"
          :class="route.path === item.path ? 'bg-white text-green-800' : 'text-green-100 hover:bg-green-700'"
        >
          <span class="text-lg">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
        <a
          v-else
          :href="item.anchor"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-green-100 hover:bg-green-700 transition-colors"
        >
          <span class="text-lg">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </a>
      </template>
    </nav>

    <div class="p-4 border-t border-green-700">
      <p class="text-sm font-medium truncate">{{ auth.user?.full_name }}</p>
      <p class="text-xs text-green-300 mb-3 capitalize">{{ auth.user?.role }}</p>
      <button @click="handleLogout" class="w-full text-xs text-green-200 hover:text-white">
        Sign out →
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const NAV_CONFIGS = {
  smallholder: [
    { path: '/farmer/dashboard', icon: '🏠', label: 'Dashboard' },
    { anchor: '#escrow-section', icon: '🔐', label: 'Escrow' },
    { anchor: '#settlements-section', icon: '💰', label: 'Settlements' },
    { anchor: '#delivery-section', icon: '🚛', label: 'Log Delivery' },
  ],
  tenant: [
    { path: '/farmer/dashboard', icon: '🏠', label: 'Dashboard' },
    { anchor: '#escrow-section', icon: '🔐', label: 'Escrow' },
    { anchor: '#settlements-section', icon: '💰', label: 'Settlements' },
    { anchor: '#delivery-section', icon: '🚛', label: 'Log Delivery' },
  ],
  landowner: [
    { path: '/landowner/dashboard', icon: '🏠', label: 'Dashboard' },
    { anchor: '#parcels-section', icon: '🗺️', label: 'Land Parcels' },
    { anchor: '#agreements-section', icon: '🤝', label: 'Agreements' },
  ],
  bank: [{ path: '/bank/dashboard', icon: '🏦', label: 'Loan Queue' }],
  admin: [{ path: '/bank/dashboard', icon: '🏦', label: 'Loan Queue' }],
  factory: [
    { path: '/factory/dashboard', icon: '🏭', label: 'Dashboard' },
    { anchor: '#deliveries-section', icon: '📦', label: 'Deliveries' },
    { anchor: '#settlements-section', icon: '💰', label: 'Settlements' },
  ],
  shopkeeper: [{ path: '/shopkeeper/dashboard', icon: '🏪', label: 'Dashboard' }],
  insurance: [{ path: '/insurance/dashboard', icon: '🛡️', label: 'Dashboard' }],
  afo: [{ path: '/afo/dashboard', icon: '📊', label: 'Dashboard' }],
}

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const navItems = computed(() => NAV_CONFIGS[auth.user?.role] || [])

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>