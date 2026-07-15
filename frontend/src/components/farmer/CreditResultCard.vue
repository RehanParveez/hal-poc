<template>
  <div class="rounded-lg overflow-hidden border">
    <div v-if="creditCheck.status === 'pending'" class="p-4 text-center">
      <div class="animate-spin h-6 w-6 border-2 border-green-600 border-t-transparent rounded-full mx-auto mb-2"></div>
      <p class="text-sm text-gray-600">Your credit check is being processed...</p>
      <p class="text-xs text-gray-400 mt-1">This usually takes less than a minute.</p>
    </div>
    <div v-else-if="creditCheck.status === 'completed' && creditCheck.is_eligible" class="p-4 bg-green-50">
      <p class="font-bold text-green-700 mb-2">Credit Check Passed ✓</p>
      <p class="text-sm text-gray-700">Maximum Loan Limit: ₨ {{ formatPKR(creditCheck.max_approved_limit_pkr) }}</p>
      <CreditTierBadge :tier="creditCheck.risk_tier" class="mt-2" />
      <p class="text-sm text-gray-600 mt-2">Your loan application can now proceed.</p>
    </div>
    <div v-else-if="creditCheck.status === 'completed' && !creditCheck.is_eligible" class="p-4 bg-red-50">
      <p class="font-bold text-red-600 mb-2">Credit Check — Not Eligible</p>
      <p class="text-sm text-gray-700">{{ rejectionReason }}</p>
      <p class="text-sm text-gray-600 mt-2">Please speak with your Numberdar or bank manager for next steps.</p>
    </div>
    <div v-else-if="creditCheck.status === 'manual_review'" class="p-4 bg-amber-50">
      <p class="font-bold text-amber-700 mb-2">Under Manual Review</p>
      <p class="text-sm text-gray-600">Our team is reviewing your file. We will contact you within 2 business days.</p>
    </div>
    <div v-else-if="creditCheck.status === 'failed'" class="p-4 bg-red-50">
      <p class="font-bold text-red-600 mb-2">Check Could Not Be Completed</p>
      <p class="text-sm text-gray-600">Please try again or contact support.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CreditTierBadge from './CreditTierBadge.vue'
const props = defineProps({ creditCheck: { type: Object, required: true } })
const rejectionReason = computed(() => {
  if (props.creditCheck.ecib_status === 'write_off') return 'A previous loan was written off. Please contact your bank.'
  if (props.creditCheck.ecib_status === 'overdue') return 'You have an overdue payment on record.'
  if (props.creditCheck.default_history_flag) return 'A previous default was found in your credit history.'
  return "Your application did not meet the bank's eligibility criteria."
})
const formatPKR = (val) => new Intl.NumberFormat('en-PK').format(Math.round(parseFloat(val) || 0))
</script>