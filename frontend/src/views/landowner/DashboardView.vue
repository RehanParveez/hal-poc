<template>
  <DashboardHero
    :eyebrow="auth.user?.district ? `${auth.user.district}, ${auth.user.province}` : 'Landowner Portal'"
    :title="`${greeting}, ${firstName}`"
    subtitle="Manage your land parcels, tenant agreements, and track your wallet."
    :stats="heroStats"
  />

  <div class="content-container -mt-8 relative z-20">
    <QuickActionsBar :actions="quickActions" />
  </div>

  <DashboardSection id="wallet-section" tone="white" eyebrow="Finances" title="Recent Transactions">
    <div class="space-y-2">
      <div v-for="txn in wallets.transactions" :key="txn.id" class="bg-white p-3 rounded shadow flex justify-between text-sm">
        <div>
          <p class="font-medium capitalize">{{ txn.txn_type }}</p>
          <p class="text-gray-500">{{ new Date(txn.created_at).toLocaleString() }}</p>
        </div>
        <p :class="txn.direction === 'credit' ? 'text-green-700' : 'text-red-600'" class="font-semibold">
          {{ txn.direction === 'credit' ? '+' : '-' }} PKR {{ formatPKR(txn.amount) }}
        </p>
      </div>
      <div v-if="isInitialLoading" class="text-gray-500">Loading transactions...</div>
      <p v-else-if="wallets.transactions.length === 0" class="text-gray-500">No transactions yet.</p>
    </div>
  </DashboardSection>

  <DashboardSection id="parcels-section" tone="tint" eyebrow="Properties" title="Land Parcels">
    <ParcelsList />
  </DashboardSection>

  <DashboardSection id="agreements-section" tone="white" eyebrow="Tenants" title="Tenant Agreements">
    <AgreementsList />
  </DashboardSection>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'

import { Wallet, Map, FileSignature, Activity } from 'lucide-vue-next'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import QuickActionsBar from '@/components/shared/QuickActionsBar.vue'

import { useAuthStore } from '@/stores/auth.js'
import { useScrollTo } from '@/composables/useScrollTo.js'

import { useWalletsStore } from '@/stores/wallets.js'
import { useCountUp } from '@/composables/useCountUp.js'

import ParcelsList from '@/components/landowner/ParcelsList.vue'
import AgreementsList from '@/components/landowner/AgreementsList.vue'

const auth = useAuthStore()
const wallets = useWalletsStore()
const scrollToSection = useScrollTo()

const animatedBalance = useCountUp(computed(() => wallets.wallet?.balance ?? 0))
const isInitialLoading = ref(true)

const formatPKR = (val) => new Intl.NumberFormat('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(val) || 0)

const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || 'Landowner')
const greeting = computed(() => {
  const hour = new Date().getHours()
  return hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
})

const heroStats = computed(() => [
  { icon: Wallet, label: 'Wallet Balance', value: `₨${formatPKR(animatedBalance.value)}` },
  { icon: Activity, label: 'Transactions', value: wallets.transactions.length.toString() }
])

const quickActions = computed(() => [
  { label: 'My Parcels', icon: Map, onClick: () => scrollToSection('parcels-section') },
  { label: 'Agreements', icon: FileSignature, onClick: () => scrollToSection('agreements-section') },
  { label: 'Wallet History', icon: Wallet, onClick: () => scrollToSection('wallet-section') },
])

onMounted(async () => {
  try {
    await wallets.fetchMyBalance()
  } catch (err) {
    console.error('Failed to load wallet balance:', err)
  }
  try {
    await wallets.fetchTransactions()
  } catch (err) {
    console.error('Failed to load transactions:', err)
  }
  isInitialLoading.value = false
})
</script>