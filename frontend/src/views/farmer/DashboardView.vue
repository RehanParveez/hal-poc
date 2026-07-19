<template>
  <div class="p-8">
    <template v-if="auth.isLoggedIn">
    <div class="mb-6">
      <button @click="showClaimModal = true" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-bold shadow">
        File Crop Damage Claim
      </button>
    </div>
    <div id="community-section"><CommunityVerificationCard /></div>
    <div id="credit-section"><CreditCheckSection /></div>
    <div id="escrow-section"><EscrowDashboardView v-if="auth.isLoggedIn" /></div>
    <div id="settlements-section"><SettlementsList v-if="auth.isLoggedIn" /></div>
    <div id="delivery-section"><LogDeliveryForm v-if="auth.isLoggedIn" /> </div>
    <div id="loan-section">
      <LoanHistory />
      <ApplyLoanForm />
    </div>
    <div id="contracts-section"><BrowseContracts /></div>
    <RequestAgreementForm v-if="auth.user?.role === 'tenant'" />
    <Transition name="modal">
      <FileClaimModal 
        v-if="showClaimModal" 
        @close="showClaimModal = false" 
        @success="showClaimModal = false" 
      />
    </Transition>
    </template>
    <p v-else class="text-gray-500">Please log in to view your dashboard.</p>
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { ref } from 'vue'
import EscrowDashboardView from './EscrowDashboardView.vue'
import SettlementsList from '@/components/farmer/SettlementsList.vue'
import LogDeliveryForm from '@/components/farmer/LogDeliveryForm.vue'
import ApplyLoanForm from '@/components/farmer/ApplyLoanForm.vue'
import LoanHistory from '@/components/farmer/LoanHistory.vue'
import BrowseContracts from '@/components/farmer/BrowseContracts.vue'
import RequestAgreementForm from '@/components/farmer/RequestAgreementForm.vue'
import FileClaimModal from '@/components/farmer/FileClaimModal.vue'
import CommunityVerificationCard from '@/components/farmer/CommunityVerificationCard.vue'
import CreditCheckSection from '@/components/farmer/CreditCheckSection.vue'

const showClaimModal = ref(false)
const auth = useAuthStore()

</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>