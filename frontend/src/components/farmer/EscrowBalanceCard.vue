<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 animate-fade-in-up">
    <div v-if="escrow.isLoading" class="text-sm text-gray-400 text-center py-6">{{ $t('common.loading') }}</div>
    <div v-else-if="escrow.error" class="text-sm text-red-600 text-center py-6">{{ escrow.error }}</div>
    <template v-else>
      <div class="flex items-start justify-between mb-4">
        <div>
          <p class="text-xs text-green-700 font-semibold uppercase tracking-wide">{{ $t('farmer.escrowBalance') }}</p>
          <p class="text-3xl font-display font-semibold text-gray-800 mt-1 tabular-nums">₨ {{ formatPKR(animatedBalance) }}</p>
          <p class="text-xs text-gray-500 mt-1 tabular-nums">{{ $t('farmer.ofTotal', { amount: formatPKR(escrow.totalFunded) }) }}</p>
        </div>
        <InsuranceBadge :status="policyStatus" />
      </div>

      <div class="mb-4">
        <div class="flex justify-between text-xs text-gray-500 mb-1">
          <span>{{ $t('farmer.spentOnInputs') }}: ₨ {{ formatPKR(escrow.totalSpent) }}</span>
          <span class="tabular-nums">{{ escrow.spendPercent }}%</span>
        </div>
        <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full bg-green-700 rounded-full transition-all duration-500" :style="{ width: escrow.spendPercent + '%' }" />
        </div>
      </div>

      <div v-if="escrow.activePhase" class="flex items-center gap-2 bg-green-50 rounded-lg px-3 py-2 border-l-2 border-gold-400">
        <span class="inline-block w-2 h-2 rounded-full bg-green-700 animate-pulse" />
        <div>
          <span class="text-xs font-semibold text-green-800">
            {{ $t('farmer.activePhase', { number: escrow.activePhase.phase_number, name: escrow.activePhase.phase_name }) }}
          </span>
          <p class="text-xs text-green-700 opacity-75">
            {{ $t('farmer.allowed') }}: {{ escrow.activePhase.allowed_input_categories?.join(', ') }}
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue' 
import { useCountUp } from '@/composables/useCountUp.js'
import { useEscrowStore } from '@/stores/escrow.js'
import InsuranceBadge from './InsuranceBadge.vue'

const escrow = useEscrowStore()
const animatedBalance = useCountUp(computed(() => escrow.remainingBalance))
const formatPKR = (val) => new Intl.NumberFormat('en-PK').format(Math.round(parseFloat(val) || 0))
</script>