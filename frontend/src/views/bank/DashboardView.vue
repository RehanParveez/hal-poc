<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold">Loan Queue</h1>
      <button @click="handleLogout" class="bg-gray-800 text-white px-4 py-2 rounded text-sm">Logout</button>
    </div>

    <select v-model="loansStore.statusFilter" @change="loansStore.fetchLoans" class="border rounded px-2 py-1 text-sm mb-4">
      <option value="">All statuses</option>
      <option value="submitted">Submitted</option>
      <option value="bank_approved">Bank Approved</option>
      <option value="disbursed">Disbursed</option>
      <option value="repaid">Repaid</option>
      <option value="rejected">Rejected</option>
    </select>

    <div v-if="loansStore.isLoading" class="text-gray-500">Loading...</div>

    <div v-else class="space-y-3">
      <LoanCard v-for="loan in loansStore.loans" :key="loan.id" :loan="loan" />
      <p v-if="loansStore.loans.length === 0" class="text-gray-500">No loan applications found.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { useLoansStore } from '@/stores/loans.js'
import LoanCard from '@/components/bank/LoanCard.vue'

const auth = useAuthStore()
const router = useRouter()
const loansStore = useLoansStore()

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  loansStore.fetchLoans()
})
</script>