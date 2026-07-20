<template>
  <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
    <div>
      <p class="text-xs font-medium text-green-700 uppercase tracking-wide">{{ auth.user?.district }} · {{ auth.user?.province }}</p>
      <h2 class="text-lg font-semibold text-gray-800">{{ pageTitle }}</h2>
    </div>
    <div class="flex items-center gap-3">
      <div v-if="showWalletPill" class="hidden sm:flex items-center gap-1.5 bg-green-50 text-green-800 text-sm font-medium px-3 py-1.5 rounded-full tabular-nums">
        <Wallet :size="14" /> ₨ {{ formattedBalance }}
      </div>
      <NotificationBell />
      <LanguageSwitcher />
      <span class="text-xs bg-green-100 text-green-800 px-3 py-1 rounded-full font-medium capitalize">{{ auth.user?.role }}</span>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useWalletsStore } from '@/stores/wallets.js'
import { Wallet } from 'lucide-vue-next'
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
const wallets = useWalletsStore()
const route = useRoute()
const pageTitle = computed(() => PATH_TITLES[route.path] || 'HAL')

const showWalletPill = computed(() => ['smallholder', 'tenant', 'landowner', 'shopkeeper'].includes(auth.user?.role))
const formattedBalance = computed(() => new Intl.NumberFormat('en-PK').format(Math.round(parseFloat(wallets.wallet?.balance) || 0)))

onMounted(() => { if (showWalletPill.value) wallets.fetchMyBalance() })

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