<template>
  <DashboardHero eyebrow="Hal" :title="$t('landowner.myWallet')" />
  <div class="p-8">
    <h2 class="text-xl font-bold mb-4">{{ $t('landowner.myWallet') }}</h2>

    <div v-if="!auth.isCorporateVerified" class="bg-amber-50 border border-amber-200 text-amber-800 p-3 rounded mb-4 text-sm">
      ⚠ {{ $t('shopkeeper.verificationPending') }}
    </div>
    
    <div v-if="wallets.wallet" class="bg-white p-4 rounded shadow mb-6">
      <p class="text-sm text-gray-500">{{ $t('landowner.currentBalance') }}</p>
      <h1 class="text-3xl font-bold text-green-700">PKR {{ formatPKR(wallets.wallet.balance) }}</h1>
    </div>

    <h3 class="font-semibold mb-2">{{ $t('landowner.recentTransactions') }}</h3>
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
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useWalletsStore } from '@/stores/wallets.js'
import { useAuthStore } from '@/stores/auth.js' 
import DashboardHero from '@/components/layout/DashboardHero.vue'

const auth = useAuthStore()
const wallets = useWalletsStore()
const isInitialLoading = ref(true)

const formatPKR = (val) => new Intl.NumberFormat('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(val) || 0)

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