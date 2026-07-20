<template>
  <DashboardHero eyebrow="Hal" :title="$t('bank.loanApprovalQueue')" :stats="heroStats" />

  <div class="flex justify-end content-container">
    <button @click="handleLogout" class="text-sm text-gray-500 hover:text-red-600 mb-4">{{ $t('common.signOut') }}</button>
  </div>

  <DashboardSection tone="white">
    <PillTabs :tabs="statusTabs" v-model="loansStore.statusFilter" @update:model-value="handleStatusChange" class="mb-6" />
      
    <div v-if="loansStore.isLoading" class="space-y-3">
      <SkeletonCard v-for="n in 3" :key="n" />
    </div>
    
    <TransitionGroup v-else name="list-item" tag="div" class="space-y-3">
      <LoanCard v-for="loan in loansStore.loans" :key="loan.id" :loan="loan" />
    </TransitionGroup>
    <p v-if="!loansStore.isLoading && loansStore.loans.length === 0" class="text-gray-500 text-center py-8">{{ $t('bank.noLoansFound') }}</p>
  </DashboardSection>

  <DashboardSection id="settlements-section" tone="tint" :eyebrow="$t('bank.factoringEyebrow')" :title="$t('bank.settlementsTitle')">
    <SettlementsOverview />
  </DashboardSection>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useLoansStore } from '@/stores/loans.js'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import LoanCard from '@/components/bank/LoanCard.vue'
import SettlementsOverview from '@/components/bank/SettlementsOverview.vue'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import SkeletonCard from '@/components/shared/SkeletonCard.vue'
import PillTabs from '@/components/shared/PillTabs.vue' 
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const statusTabs = computed(() => [
  { label: t('bank.statusAll'), value: '' }, { label: t('bank.statusSubmitted'), value: 'submitted' }, { label: t('bank.statusApproved'), value: 'bank_approved' },
  { label: t('bank.statusDisbursed'), value: 'disbursed' }, { label: t('bank.statusRepaid'), value: 'repaid' }, { label: t('bank.statusRejected'), value: 'rejected' },
])

const loansStore = useLoansStore()
const router = useRouter()
const auth = useAuthStore()
const heroStats = computed(() => [
  { label: t('bank.pendingReview'), value: loansStore.loans.filter(l => l.status === 'submitted').length },
  { label: t('bank.approved'), value: loansStore.loans.filter(l => l.status === 'bank_approved').length },
  { label: t('bank.disbursed'), value: loansStore.loans.filter(l => l.status === 'disbursed').length },
])

function handleLogout() {
  auth.logout()
  router.push('/login')
}

function handleStatusChange() {
  loansStore.fetchLoans({ status: loansStore.statusFilter || undefined })
}

onMounted(() => {
  loansStore.fetchLoans()
})
</script>