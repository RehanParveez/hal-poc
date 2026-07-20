<template>
  <template v-if="auth.isLoggedIn">
    <DashboardHero
      :eyebrow="`${auth.user?.district}, ${auth.user?.province}`"
      :title="`${greeting}, ${firstName}`"
      :subtitle="$t('farmer.dashboardSubtitle')"
      :stats="heroStats"
    >
      <template #action>
        <button @click="showClaimModal = true" class="btn-danger">{{ $t('farmer.fileClaimBtn') }}</button>
      </template>
    </DashboardHero>

    <div class="content-container -mt-8 relative z-20">
      <QuickActionsBar :actions="quickActions" />
    </div>

    <DashboardSection id="community-section" tone="white" eyebrow="Trust & Eligibility" title="Community Verification">
      <CommunityVerificationCard />
    </DashboardSection>

    <DashboardSection id="credit-section" tone="tint" eyebrow="Before You Borrow" title="Credit Check">
      <CreditCheckSection />
    </DashboardSection>

    <DashboardSection id="escrow-section" tone="white" eyebrow="Your Funds" title="Escrow Account">
      <EscrowDashboardView />
    </DashboardSection>

    <DashboardSection id="loan-section" tone="tint" eyebrow="Financing" title="Loans">
      <LoanHistory />
      <ApplyLoanForm />
    </DashboardSection>

    <DashboardSection id="contracts-section" tone="white" eyebrow="Harvest Buyers" title="Open Contracts">
      <BrowseContracts />
    </DashboardSection>

    <DashboardSection v-if="auth.user?.role === 'tenant'" id="agreement-section" tone="tint" eyebrow="Land" title="Tenant Agreement">
      <RequestAgreementForm />
    </DashboardSection>

    <DashboardSection id="delivery-section" tone="white" eyebrow="Log Your Harvest" title="Delivery">
      <LogDeliveryForm />
    </DashboardSection>

    <DashboardSection id="settlements-section" tone="tint" eyebrow="Getting Paid" title="Settlements">
      <SettlementsList />
    </DashboardSection>

    <Transition name="modal">
      <FileClaimModal v-if="showClaimModal" @close="showClaimModal = false" @success="showClaimModal = false" />
    </Transition>
  </template>
  <p v-else class="content-container py-16 text-gray-500">Please log in to view your dashboard.</p>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Wallet, Landmark, FileSignature, Truck } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth.js'
import { useEscrowStore } from '@/stores/escrow.js'
import { useLoansStore } from '@/stores/loans.js'
import { useScrollTo } from '@/composables/useScrollTo.js'

import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import QuickActionsBar from '@/components/shared/QuickActionsBar.vue'

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

const { t } = useI18n()
const showClaimModal = ref(false)
const auth = useAuthStore()
const escrow = useEscrowStore()
const loans = useLoansStore()
const scrollToSection = useScrollTo()

const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || 'Farmer')

const greeting = computed(() => {
  const hour = new Date().getHours()
  return hour < 12 ? t('farmer.goodMorning') : hour < 17 ? t('farmer.goodAfternoon') : t('farmer.goodEvening')
})

const heroStats = computed(() => [
  { icon: Wallet, label: t('farmer.escrowBalance'), value: `₨${new Intl.NumberFormat('en-PK').format(Math.round(escrow.remainingBalance || 0))}` },
  { icon: Landmark, label: t('farmer.activeLoans'), value: loans.myLoans.filter(l => ['disbursed', 'repaid'].includes(l.status)).length },
  { icon: FileSignature, label: t('farmer.creditTier'), value: (auth.user?.credit_tier || 'unverified').replace('_', ' ') },
])

const quickActions = computed(() => [
  { label: t('farmer.qaApplyLoan'), icon: Landmark, onClick: () => scrollToSection('loan-section') },
  { label: t('farmer.qaViewEscrow'), icon: Wallet, onClick: () => scrollToSection('escrow-section') },
  { label: t('farmer.qaLogDelivery'), icon: Truck, onClick: () => scrollToSection('delivery-section') },
  { label: t('farmer.qaBrowseContracts'), icon: FileSignature, onClick: () => scrollToSection('contracts-section') },
])

</script>