<template>
  <div class="p-8">
    <div class="mb-6">
      <button @click="showClaimModal = true" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-bold shadow">
        File Crop Damage Claim
      </button>
    </div>
    <div id="escrow-section"><EscrowDashboardView v-if="auth.isLoggedIn" /></div>
    <div id="settlements-section"><SettlementsList v-if="auth.isLoggedIn" /></div>
    <div id="delivery-section"><LogDeliveryForm v-if="auth.isLoggedIn" /> </div>
    <div id="loan-section">
      <LoanHistory />
      <ApplyLoanForm />
    </div>
    <div id="contracts-section"><BrowseContracts /></div>
    <RequestAgreementForm v-if="auth.user?.role === 'tenant'" />
    <FileClaimModal 
      v-if="showClaimModal" 
      @close="showClaimModal = false" 
      @success="showClaimModal = false" 
    />
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
import { ref } from 'vue'
import FileClaimModal from '@/components/farmer/FileClaimModal.vue'

const showClaimModal = ref(false)
const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>