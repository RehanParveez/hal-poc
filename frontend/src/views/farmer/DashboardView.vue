<template>
  <div class="p-8">
    <div id="escrow-section"><EscrowDashboardView v-if="auth.isLoggedIn" /></div>
    <div id="settlements-section"><SettlementsList v-if="auth.isLoggedIn" /></div>
    <div id="delivery-section"><LogDeliveryForm v-if="auth.isLoggedIn" /> </div>
    <div id="loan-section">
      <LoanHistory />
      <ApplyLoanForm />
    </div>
    <div id="contracts-section"><BrowseContracts /></div>
    <RequestAgreementForm v-if="auth.user?.role === 'tenant'" />
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import EscrowDashboardView from './EscrowDashboardView.vue'
import SettlementsList from '@/components/farmer/SettlementsList.vue'
import LogDeliveryForm from '@/components/farmer/LogDeliveryForm.vue'
import ApplyLoanForm from '@/components/farmer/ApplyLoanForm.vue'
import LoanHistory from '@/components/farmer/LoanHistory.vue'
import BrowseContracts from '@/components/farmer/BrowseContracts.vue'
import RequestAgreementForm from '@/components/farmer/RequestAgreementForm.vue'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>