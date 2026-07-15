<template>
  <div class="border rounded-lg p-4">
    <p v-if="!creditCheck" class="text-sm text-gray-500">No credit check has been run for this application. Credit check is required before disbursement.</p>
    <div v-else-if="creditCheck.status === 'pending'" class="text-center py-3">
      <div class="animate-spin h-5 w-5 border-2 border-green-600 border-t-transparent rounded-full mx-auto mb-2"></div>
      <p class="text-sm text-gray-500">Credit check in progress...</p>
    </div>
    <div v-else-if="creditCheck.status === 'completed'">
      <div class="grid grid-cols-2 gap-4 text-sm mb-3">
        <div>
          <p class="font-semibold text-xs text-gray-500 uppercase">Tasdeeq</p>
          <p class="text-2xl font-bold">{{ creditCheck.credit_score ?? '—' }}</p>
          <CreditTierBadge :tier="creditCheck.risk_tier" size="sm" class="mt-1" />
        </div>
        <div>
          <p class="font-semibold text-xs text-gray-500 uppercase">eCIB</p>
          <p class="text-sm">Exposure: PKR {{ creditCheck.total_outstanding_debt ?? 0 }}</p>
          <p class="text-sm capitalize">Status: {{ creditCheck.ecib_status ?? '—' }}</p>
        </div>
      </div>
      <div class="bg-gray-50 rounded p-3 text-sm mb-2">
        <p><strong>Eligible:</strong> {{ creditCheck.is_eligible ? 'Yes' : 'No' }}</p>
        <p><strong>Max Approved Limit:</strong> PKR {{ creditCheck.max_approved_limit_pkr ?? 0 }}</p>
      </div>
      <button v-if="creditCheck.raw_bank_response" @click="showRaw = !showRaw" class="text-xs text-green-700 hover:underline">
        {{ showRaw ? 'Hide' : 'Show' }} raw response
      </button>
      <pre v-if="showRaw" class="text-xs bg-gray-900 text-green-400 p-2 rounded mt-2 overflow-x-auto">{{ JSON.stringify(creditCheck.raw_bank_response, null, 2) }}</pre>
    </div>
    <div v-else-if="creditCheck.status === 'manual_review'" class="bg-amber-50 p-3 rounded text-sm text-amber-700">Manual review required.</div>
    <div v-else-if="creditCheck.status === 'failed'" class="bg-red-50 p-3 rounded text-sm text-red-700">Bureau check failed. Retry or proceed manually.</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CreditTierBadge from '../../components/shared/CreditTierBadge.vue'
defineProps({ creditCheck: { type: Object, default: null } })
const showRaw = ref(false)
</script>