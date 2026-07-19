<template>
  <DashboardHero eyebrow="Bank Portal" title="Loan Approval Queue" subtitle="Review, approve, and disburse farmer loan applications." :stats="heroStats" />

  <DashboardSection tone="white">
    <select v-model="loansStore.statusFilter" @change="handleStatusChange" class="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white mb-6">
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
    <TransitionGroup v-else name="list-item" tag="div" class="space-y-3">
      <LoanCard v-for="loan in loansStore.loans" :key="loan.id" :loan="loan" />
    </TransitionGroup>
    <p v-if="!loansStore.isLoading && loansStore.loans.length === 0" class="text-gray-500 text-center py-8">No loan applications found.</p>
  </DashboardSection>

  <DashboardSection id="settlements-section" tone="tint" eyebrow="Factoring" title="Settlements">
    <SettlementsOverview />
  </DashboardSection>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useLoansStore } from '@/stores/loans.js'
import LoanCard from '@/components/bank/LoanCard.vue'
import SettlementsOverview from '@/components/bank/SettlementsOverview.vue'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import SkeletonCard from '@/components/shared/SkeletonCard.vue'

const loansStore = useLoansStore()

const heroStats = computed(() => [
  { label: 'Pending Review', value: loansStore.loans.filter(l => l.status === 'submitted').length },
  { label: 'Approved', value: loansStore.loans.filter(l => l.status === 'bank_approved').length },
  { label: 'Disbursed', value: loansStore.loans.filter(l => l.status === 'disbursed').length },
])

function handleStatusChange() {
  loansStore.fetchLoans({ status: loansStore.statusFilter || undefined })
}

onMounted(() => {
  loansStore.fetchLoans()
})
</script>