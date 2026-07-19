<template>
  <DashboardHero eyebrow="Bank Portal" title="Loan Approval Queue" subtitle="Review, approve, and disburse farmer loan applications." :stats="heroStats" />

  <DashboardSection tone="white">
    <PillTabs :tabs="statusTabs" v-model="loansStore.statusFilter" @update:model-value="handleStatusChange" class="mb-6" />
      
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
import PillTabs from '@/components/shared/PillTabs.vue' 
const statusTabs = [
  { label: 'All', value: '' }, { label: 'Submitted', value: 'submitted' }, { label: 'Approved', value: 'bank_approved' },
  { label: 'Disbursed', value: 'disbursed' }, { label: 'Repaid', value: 'repaid' }, { label: 'Rejected', value: 'rejected' },
]

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