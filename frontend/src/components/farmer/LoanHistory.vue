<template>
  <div class="mt-6">
    <h2 class="text-lg font-bold mb-3">My Loan Applications</h2>
    <div class="space-y-2">
      <div v-for="loan in loans.myLoans" :key="loan.id" class="bg-white p-3 rounded shadow flex justify-between text-sm">
        <div>
          <p class="font-medium">Requested: PKR {{ loan.requested_amount }}</p>
          <p class="text-gray-500">{{ loan.acres_applied_for }} acres</p>
        </div>
        <StatusBadge :status="loan.status" class="self-start" />
      </div>
      <p v-if="loans.myLoans.length === 0" class="text-gray-500">No loan applications yet.</p>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from '@/components/shared/StatusBadge.vue'
import { onMounted } from 'vue'
import { useLoansStore } from '@/stores/loans.js'

const loans = useLoansStore()

onMounted(() => {
  loans.fetchAllMyLoans()
})
</script>