<template>
  <div class="p-8">
    <h2 class="text-xl font-bold mb-4">My Wallet</h2>
    <div v-if="wallets.wallet" class="bg-white p-4 rounded shadow mb-6">
      <p class="text-sm text-gray-500">Current Balance</p>
      <h1 class="text-3xl font-bold text-green-700">PKR {{ wallets.wallet.balance }}</h1>
    </div>
    <h3 class="font-semibold mb-2">Recent Transactions</h3>
    <div class="space-y-2">
      <div v-for="txn in wallets.transactions" :key="txn.id" class="bg-white p-3 rounded shadow flex justify-between text-sm">
        <div>
          <p class="font-medium capitalize">{{ txn.txn_type }}</p>
          <p class="text-gray-500">{{ new Date(txn.created_at).toLocaleString() }}</p>
        </div>
        <p :class="txn.direction === 'credit' ? 'text-green-700' : 'text-red-600'" class="font-semibold">
          {{ txn.direction === 'credit' ? '+' : '-' }} PKR {{ txn.amount }}
        </p>
      </div>
      <p v-if="wallets.transactions.length === 0" class="text-gray-500">No transactions yet.</p>
    </div>
    <div id="parcels-section"><ParcelsList /></div>
    <div id="agreements-section"><AgreementsList /></div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useWalletsStore } from '@/stores/wallets.js'

import ParcelsList from '@/components/landowner/ParcelsList.vue'
import AgreementsList from '@/components/landowner/AgreementsList.vue'

const wallets = useWalletsStore()

onMounted(async () => {
  await wallets.fetchMyBalance()
  await wallets.fetchTransactions()
})
</script>