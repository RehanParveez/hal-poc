<template>
  <DashboardHero
  :eyebrow="auth.user?.district ? `${auth.user.district}, ${auth.user.province}` : 'Landowner Portal'"
  :title="`${greeting}, ${firstName}`"
  :subtitle="$t('landowner.dashboardSubtitle')"
  :stats="heroStats"
/>

  <div class="content-container -mt-8 relative z-20">
    <QuickActionsBar :actions="quickActions" />
  </div>

  <DashboardSection id="wallet-section" tone="white" :eyebrow="$t('landowner.financesEyebrow')" :title="$t('landowner.recentTransactions')">
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
      <div v-if="isInitialLoading" class="text-gray-500">{{ $t('landowner.loadingTransactions') }}</div>
      <p v-else-if="wallets.transactions.length === 0" class="text-gray-500">{{ $t('landowner.noTransactions') }}</p>
    </div>
  </DashboardSection>

  <DashboardSection id="parcels-section" tone="tint" :eyebrow="$t('landowner.propertiesEyebrow')" :title="$t('landowner.landParcelsTitle')">
    <ParcelsList />
  </DashboardSection>

  <DashboardSection id="agreements-section" tone="white" :eyebrow="$t('landowner.tenantsEyebrow')" :title="$t('landowner.tenantAgreements')">
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
import { useI18n } from 'vue-i18n'

const { t } = useI18n() 
const auth = useAuthStore()
const wallets = useWalletsStore()
const scrollToSection = useScrollTo()

const animatedBalance = useCountUp(computed(() => wallets.wallet?.balance ?? 0))
const isInitialLoading = ref(true)

const formatPKR = (val) => new Intl.NumberFormat('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(val) || 0)

const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || t('landowner.landownerFallback'))

const greeting = computed(() => {
  const hour = new Date().getHours()
  return hour < 12 ? t('landowner.goodMorning') : hour < 17 ? t('landowner.goodAfternoon') : t('landowner.goodEvening')
})

const heroStats = computed(() => [
  { icon: Wallet, label: t('landowner.walletBalance'), value: `₨${formatPKR(animatedBalance.value)}` },
  { icon: Activity, label: t('landowner.transactions'), value: wallets.transactions.length.toString() }
])

const quickActions = computed(() => [
  { label: t('landowner.qaMyParcels'), icon: Map, onClick: () => scrollToSection('parcels-section') },
  { label: t('landowner.qaAgreements'), icon: FileSignature, onClick: () => scrollToSection('agreements-section') },
  { label: t('landowner.qaWalletHistory'), icon: Wallet, onClick: () => scrollToSection('wallet-section') },
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