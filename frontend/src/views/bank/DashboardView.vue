<template>
  <div class="p-8">
    <div class="flex justify-end">
      <button @click="handleLogout" class="text-sm text-gray-500 hover:text-red-600 mb-4">
        Logout
      </button>
    </div>
    <select v-model="loansStore.statusFilter" @change="handleStatusChange" class="border rounded px-2 py-1 text-sm mb-4">
      <option value="">All statuses</option>
      <option value="submitted">Submitted</option>
      <option value="bank_approved">Bank Approved</option>
      <option value="disbursed">Disbursed</option>
      <option value="repaid">Repaid</option>
      <option value="rejected">Rejected</option>
    </select>

    <div v-if="loansStore.isLoading" class="space-y-3">
     <SkeletonCard v-for="n in 3" :key="n" />
    </div>

    <div v-else class="space-y-3">
      <LoanCard v-for="loan in loansStore.loans" :key="loan.id" :loan="loan" />
      <p v-if="loansStore.loans.length === 0" class="text-gray-500">No loan applications found.</p>
    </div>
    <div id="settlements-section"><SettlementsOverview /></div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { useLoansStore } from '@/stores/loans.js'
import LoanCard from '@/components/bank/LoanCard.vue'
import SettlementsOverview from '@/components/bank/SettlementsOverview.vue'
import SkeletonCard from '@/components/shared/SkeletonCard.vue'

const auth = useAuthStore()
const router = useRouter()
const loansStore = useLoansStore()

function handleStatusChange() {
  loansStore.fetchLoans({ status: loansStore.statusFilter || undefined })
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  loansStore.fetchLoans()
})
</script>