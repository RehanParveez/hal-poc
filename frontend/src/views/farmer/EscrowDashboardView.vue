<template>
  <div class="p-6">
    <h2 class="text-xl font-bold mb-4">My Escrow Account</h2>
    <div v-if="escrow.wallet" class="bg-white p-4 rounded shadow">
      <p class="text-sm text-gray-500">Remaining Balance</p>
      <h1 class="text-3xl font-bold text-green-700">PKR {{ escrow.wallet.remaining_balance }}</h1>

      <div class="mt-4 border-t pt-4">
        <p>Active Phase: <strong>{{ escrow.wallet.active_phase?.phase_name || 'None' }}</strong></p>
        <button @click="showModal = true" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded">
          Pay Shopkeeper
        </button>
      </div>
    </div>
    <p v-else-if="!loans.activeLoan" class="text-gray-500">No disbursed loan found yet.</p>

    <PaymentModal
      v-if="showModal"
      @close="showModal = false"
      @success="handleSuccess"
      :escrowId="loans.activeLoan?.escrow_id"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useEscrowStore } from '@/stores/escrow.js'
import { useLoansStore } from '@/stores/loans.js'
import { useAuthStore } from '@/stores/auth.js'
import PaymentModal from '@/components/PaymentModal.vue'

const escrow = useEscrowStore()
const loans = useLoansStore()
const auth = useAuthStore()
const showModal = ref(false)

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
})

const handleSuccess = () => {
  showModal.value = false
  escrow.refreshWallet(loans.activeLoan.escrow_id)
  escrow.fetchCaps(loans.activeLoan.escrow_id)
}
</script>