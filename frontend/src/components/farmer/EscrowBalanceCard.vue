<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
    <div v-if="escrow.isLoading" class="text-sm text-gray-400 text-center py-6">Loading escrow balance…</div>
    <div v-else-if="escrow.error" class="text-sm text-red-600 text-center py-6">{{ escrow.error }}</div>
    <template v-else>
     <div class="flex items-start justify-between mb-4">
      <div>
      
        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Escrow Balance</p>
        <p class="text-3xl font-bold text-gray-800 mt-1">₨ {{ formatPKR(escrow.remainingBalance) }}</p>
        <p class="text-xs text-gray-500 mt-1">of ₨ {{ formatPKR(escrow.totalFunded) }} total</p>
      </div>
      <div class="flex flex-col items-end gap-2">
      <InsuranceBadge :status="myPolicyStatus" />
      <CreditTierBadge :tier="auth.user?.credit_tier" size="sm" />
      </div>
    </div>

    <div class="mb-4">
      <div class="flex justify-between text-xs text-gray-500 mb-1">
        <span>Spent on inputs: ₨ {{ formatPKR(escrow.totalSpent) }}</span>
        <span>{{ escrow.spendPercent }}%</span>
      </div>
      <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div class="h-full bg-green-600 rounded-full transition-all duration-500" :style="{ width: escrow.spendPercent + '%' }" />
      </div>
    </div>

    <div v-if="escrow.activePhase" class="flex items-center gap-2 bg-green-50 rounded-lg px-3 py-2">
      <span class="inline-block w-2 h-2 rounded-full bg-green-600 animate-pulse" />
      <div>
        <span class="text-xs font-semibold text-green-700">
          Phase {{ escrow.activePhase.phase_number }}: {{ escrow.activePhase.phase_name }}
        </span>
        <p class="text-xs text-green-700 opacity-75">
          Allowed: {{ escrow.activePhase.allowed_input_categories?.join(', ') }}
        </p>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { useEscrowStore } from '@/stores/escrow.js'
import { useInsuranceStore } from '@/stores/insurance.js'
import { onMounted, computed } from 'vue' 
import InsuranceBadge from './InsuranceBadge.vue'
import CreditTierBadge from './CreditTierBadge.vue'
import { useAuthStore } from '@/stores/auth.js' 

const escrow = useEscrowStore()
const auth = useAuthStore()
const insurance = useInsuranceStore()
const formatPKR = (val) => new Intl.NumberFormat('en-PK').format(Math.round(parseFloat(val) || 0))

const myPolicyStatus = computed(() => {
  const policy = insurance.policies.find((p) => p.loan_id === escrow.wallet?.loan_id)
  return policy?.status ?? null
})

onMounted(() => {
  if (insurance.policies.length === 0) {
    insurance.fetchPolicies()
  }
})
</script>