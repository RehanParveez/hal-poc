<template>
  <DashboardHero eyebrow="Hal" :title="$t('insurance.dashboardTitle')" />
 
  <div class="content-container -mt-8 relative z-20">
    <QuickActionsBar :actions="quickActions" />
  </div>
 
  <DashboardSection id="claims-section" tone="white" eyebrow="Claims" title="Incoming Damage Claims">
      <div v-if="isInitialLoading" class="text-gray-500">Loading...</div>
      <div v-else class="space-y-3">
        <div v-for="claim in insurance.claims" :key="claim.id" class="bg-white p-4 rounded shadow">
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold">{{ claim.farmer_name }}</p>
              <p class="text-sm text-gray-500">Claim Amount: PKR {{ claim.claim_amount }}</p>
            </div>
            <StatusBadge :status="claim.status" />
          </div>
 
          <div v-if="claim.status === 'pending'" class="mt-3 border-t pt-3 space-y-2">
            <input v-model.number="reviewForm[claim.id].approved_amount" type="number" min="0" step="0.01" :placeholder="$t('insurance.approvedAmountPlaceholder')" class="border rounded px-2 py-1 text-sm w-full" />
            <input v-model="reviewForm[claim.id].reviewer_note" type="text" :placeholder="$t('insurance.reviewerNotePlaceholder')" class="border rounded px-2 py-1 text-sm w-full" />
            <div class="flex gap-2">
              <button @click="handleReview(claim.id, 'approved')" :disabled="reviewForm[claim.id].isSubmitting || !reviewForm[claim.id].approved_amount" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">
               {{ reviewForm[claim.id].isSubmitting ? $t('common.submitting') : $t('insurance.approve') }}
              </button>
              <button @click="handleReview(claim.id, 'rejected')" :disabled="reviewForm[claim.id].isSubmitting" class="bg-red-600 text-white px-3 py-1.5 rounded text-sm">
               {{ reviewForm[claim.id].isSubmitting ? $t('common.submitting') : $t('insurance.reject') }}
              </button>
            </div>
            <p v-if="reviewForm[claim.id].error" class="text-red-600 text-sm mt-1">{{ reviewForm[claim.id].error }}</p>
          </div>
        </div>
        <p v-if="!isInitialLoading && insurance.claims.length === 0" class="text-gray-500">{{ $t('insurance.noClaims') }}</p>
      </div>
    </DashboardSection>
 
  <DashboardSection id="policies-section" tone="tint" eyebrow="Portfolio" title="All Policies">
      <div v-if="isInitialLoading" class="text-gray-500">{{ $t('common.loading') }}</div>
      <div class="space-y-2">
        <div v-for="p in insurance.policies" :key="p.id" class="bg-white p-3 rounded shadow flex justify-between text-sm">
          <span>{{ p.farmer_name }} — Coverage PKR {{ p.coverage_amount }}</span>
          <StatusBadge :status="p.status" />
        </div>
        <p v-if="!isInitialLoading && insurance.policies.length === 0" class="text-gray-500">{{ $t('insurance.noPolicies') }}</p>
      </div>
  </DashboardSection>
</template>
 
<script setup>
import { onMounted, reactive, ref, watch, computed } from 'vue'
import { useInsuranceStore } from '@/stores/insurance.js'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import { FileWarning, ShieldCheck, Activity } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth.js'
import { useScrollTo } from '@/composables/useScrollTo.js'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import QuickActionsBar from '@/components/shared/QuickActionsBar.vue'
 
const insurance = useInsuranceStore()
const auth = useAuthStore()
const scrollToSection = useScrollTo()
const reviewForm = reactive({})
const isInitialLoading = ref(true)
 
const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || 'Agent')

const greeting = computed(() => {
  const hour = new Date().getHours()
  return hour < 12 ? t('insurance.goodMorning') : hour < 17 ? t('insurance.goodAfternoon') : t('insurance.goodEvening')
})
 
const heroStats = computed(() => [
  { icon: FileWarning, label: t('insurance.pendingClaims'), value: insurance.claims.filter(c => c.status === 'pending').length },
  { icon: ShieldCheck, label: t('insurance.activePolicies'), value: insurance.policies.length },
  { icon: Activity, label: t('insurance.totalClaims'), value: insurance.claims.length }
])
 
const quickActions = computed(() => [
  { label: t('insurance.qaReviewClaims'), icon: FileWarning, onClick: () => scrollToSection('claims-section') },
  { label: t('insurance.qaViewPolicies'), icon: ShieldCheck, onClick: () => scrollToSection('policies-section') },
])
 
watch(
  () => insurance.claims,
  (claims) => {
    claims.forEach((c) => {
      if (!reviewForm[c.id]) {
        reviewForm[c.id] = { approved_amount: 0, reviewer_note: '', isSubmitting: false, error: '' }
      }
    })
  },
  { immediate: true }
)
 
onMounted(async () => {
  try {
    await Promise.all([
      insurance.fetchClaims(),
      insurance.fetchPolicies()
    ])
  } catch (err) {
    console.error('Failed to load insurance dashboard data:', err)
  } finally {
    isInitialLoading.value = false
  }
})
 
async function handleReview(claimId, decision) {
  const form = reviewForm[claimId]
  if (decision === 'approved' && !form.approved_amount) return
  form.isSubmitting = true
  form.error = ''
  try {
    await insurance.reviewClaim(claimId, decision, form.approved_amount, form.reviewer_note)
  } catch (err) {
    form.error = err.response?.data?.error ?? 'Failed to review claim.'
  } finally {
    form.isSubmitting = false
  }
}
</script>