<template>
  <div class="p-6">
    <h2 class="text-xl font-bold mb-4">My Escrow Account</h2>
    <div v-if="isInitialLoading" class="text-gray-500">Loading your escrow account...</div>
    <template v-else>
    <EscrowBalanceCard v-if="escrow.wallet" />
    <div v-if="escrow.wallet" class="mt-4">
      <button @click="showModal = true" class="bg-blue-600 text-white px-4 py-2 rounded">Pay Shopkeeper</button>
    </div>
    <div v-if="escrow.wallet" class="mt-6">
      <MilestoneProgressBar />
    </div>
    <p v-else-if="!loans.activeLoan" class="text-gray-500">No disbursed loan found yet.</p>
    <p v-else class="text-red-600">Could not load your escrow account. Please refresh the page.</p>
    </template>
    <PaymentModal v-if="showModal" @close="showModal = false" @success="handleSuccess" :escrowId="loans.activeLoan?.escrow_id" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useEscrowStore } from '@/stores/escrow.js'
import { useLoansStore } from '@/stores/loans.js'
import { useAuthStore } from '@/stores/auth.js'
import PaymentModal from '@/components/PaymentModal.vue'
import EscrowBalanceCard from '@/components/farmer/EscrowBalanceCard.vue'
import MilestoneProgressBar from '@/components/farmer/MilestoneProgressBar.vue'

const escrow = useEscrowStore()
const loans = useLoansStore()
const auth = useAuthStore()
const showModal = ref(false)
const isInitialLoading = ref(true)

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      await loans.fetchMyLoan()
      if (loans.activeLoan?.escrow_id) {
        await escrow.fetchWallet(loans.activeLoan.escrow_id)
        await escrow.fetchCaps(loans.activeLoan.escrow_id)
      }
    } catch (error) {
      console.error('failed to fetch dashboard data', error)
    }
  }
  isInitialLoading.value = false
})

const handleSuccess = () => {
  showModal.value = false
  escrow.refreshWallet(loans.activeLoan.escrow_id)
  escrow.fetchCaps(loans.activeLoan.escrow_id)
}
</script>