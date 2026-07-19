<template>
  <aside class="w-64 min-h-screen bg-slate-900 text-slate-300 flex flex-col shadow-xl">
    <div class="p-5 border-b border-slate-800 bg-slate-950 field-texture relative overflow-hidden">
      <div class="relative z-10 flex items-center gap-2">
        <Wheat :size="22" class="text-gold-400" />
        <h1 class="text-xl font-semibold text-white tracking-wide">Hal</h1>
      </div>
      <p class="relative z-10 text-xs text-slate-500 mt-1">Pakistan</p>
    </div>

    <nav class="flex-1 py-4 px-3 space-y-1">
      <template v-for="item in navItems" :key="item.path || item.anchor">
        <router-link
          v-if="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors border-l-2"
          :class="route.path === item.path
            ? 'bg-slate-800 text-white font-semibold border-gold-400'
            : 'text-slate-400 border-transparent hover:bg-slate-800/60 hover:text-white'"
        >
          <component :is="item.icon" :size="18" class="flex-shrink-0" />
          <span>{{ item.label }}</span>
        </router-link>
        <a v-else :href="item.anchor"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-slate-400 border-l-2 border-transparent hover:bg-slate-800/60 hover:text-white transition-colors">
          <component :is="item.icon" :size="18" class="flex-shrink-0" />
          <span>{{ item.label }}</span>
        </a>
      </template>
    </nav>

    <div class="p-4 border-t border-slate-800 bg-slate-950/50">
      <p class="text-sm font-medium text-slate-200 truncate">{{ auth.user?.full_name }}</p>
      <p class="text-xs text-slate-500 mb-3 capitalize">{{ auth.user?.role }}</p>
      <button @click="handleLogout" class="w-full text-xs text-slate-400 hover:text-white transition-colors">
        Sign out →
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import {
  Home, Wallet, Coins, Truck, FileText, FileSignature, MapPin,
  Handshake, Landmark, ShieldCheck, Wheat, SlidersHorizontal,
  ListChecks, ClipboardCheck,
} from 'lucide-vue-next'   // NEW

const NAV_CONFIGS = {
  smallholder: [
    { path: '/farmer/dashboard', icon: Home, label: 'Dashboard' },
    { anchor: '#escrow-section', icon: Wallet, label: 'Escrow' },
    { anchor: '#settlements-section', icon: Coins, label: 'Settlements' },
    { anchor: '#delivery-section', icon: Truck, label: 'Log Delivery' },
    { anchor: '#loan-section', icon: Landmark, label: 'My Loans' },
    { anchor: '#contracts-section', icon: FileSignature, label: 'Contracts' },
  ],
  tenant: [
    { path: '/farmer/dashboard', icon: Home, label: 'Dashboard' },
    { anchor: '#escrow-section', icon: Wallet, label: 'Escrow' },
    { anchor: '#settlements-section', icon: Coins, label: 'Settlements' },
    { anchor: '#delivery-section', icon: Truck, label: 'Log Delivery' },
    { anchor: '#loan-section', icon: Landmark, label: 'My Loans' },
    { anchor: '#contracts-section', icon: FileSignature, label: 'Contracts' },
  ],
  landowner: [
    { path: '/landowner/dashboard', icon: Home, label: 'Dashboard' },
    { anchor: '#parcels-section', icon: MapPin, label: 'Land Parcels' },
    { anchor: '#agreements-section', icon: Handshake, label: 'Agreements' },
  ],
  bank: [
    { path: '/bank/dashboard', icon: Landmark, label: 'Loan Queue' },
    { anchor: '#settlements-section', icon: Coins, label: 'Settlements' },
  ],
  admin: [{ path: '/bank/dashboard', icon: Landmark, label: 'Loan Queue' }],
  factory: [
    { path: '/factory/dashboard', icon: Home, label: 'Dashboard' },
    { anchor: '#deliveries-section', icon: Truck, label: 'Deliveries' },
    { anchor: '#settlements-section', icon: Coins, label: 'Settlements' },
    { anchor: '#post-contract-section', icon: FileSignature, label: 'Post Contract' },
  ],
  shopkeeper: [{ path: '/shopkeeper/dashboard', icon: Home, label: 'Dashboard' }],
  insurance: [
    { path: '/insurance/dashboard', icon: Home, label: 'Dashboard' },
    { anchor: '#claims-section', icon: ShieldCheck, label: 'Claims' },
    { anchor: '#policies-section', icon: FileText, label: 'Policies' },
  ],
  afo: [
    { path: '/afo/dashboard', icon: Home, label: 'Dashboard' },
    { anchor: '#crop-types-section', icon: Wheat, label: 'Crop Types' },
    { anchor: '#input-caps-section', icon: SlidersHorizontal, label: 'Spending Caps' },
    { anchor: '#milestones-section', icon: ListChecks, label: 'Milestones' },
  ],
  numberdar: [
    { path: '/numberdar/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/numberdar/queue', icon: ClipboardCheck, label: 'Verification Queue' },
  ],
}

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const navItems = computed(() => NAV_CONFIGS[auth.user?.role] || [])

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>