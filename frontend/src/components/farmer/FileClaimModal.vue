<template>
  <div class="fixed inset-0 bg-slate-900/70 flex items-center justify-center p-4 z-50">
    <div class="bg-slate-950 border border-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
      <h3 class="text-lg font-bold text-slate-200 mb-4">File Crop Insurance Claim</h3>
      
      <label class="block text-xs font-semibold text-slate-400 mb-1">Select Your Policy</label>
        <select v-model="form.policy_id" class="w-full bg-slate-900 border border-slate-800 rounded p-2 text-sm text-slate-200 mb-3">
          <option value="">Select a policy</option>
          <option v-for="p in insurance.policies" :key="p.id" :value="p.id">
            Coverage PKR {{ p.coverage_amount }} — {{ p.status }}
          </option>
        </select>
        <p v-if="!insurance.isLoading && insurance.policies.length === 0" class="text-xs text-amber-500 mb-3">
          You don't have any active insurance policies yet.
        </p>

      <label class="block text-xs font-semibold text-slate-400 mb-1">Reason for Loss</label>
      <select v-model="form.reason" class="w-full bg-slate-900 border border-slate-800 rounded p-2 text-sm text-slate-200 mb-3">
        <option value="">Select event type...</option>
        <option value="heavy_rainfall_and_flood">Flash Flooding / Heavy Rainfall</option>
        <option value="extended_drought_season">Extended Drought Condition</option>
        <option value="severe_locust_pest_attack">Locust / Pest Outbreak</option>
      </select>

      <label class="block text-xs font-semibold text-slate-400 mb-1">Requested Claim Amount (PKR)</label>
      <input v-model.number="form.claim_amount" type="number" min="1" placeholder="e.g. 50000" 
            class="w-full bg-slate-900 border border-slate-800 rounded p-2 text-sm text-slate-200 mb-4" />

      <div class="flex gap-2">
        <button @click="handleSubmit" :disabled="insurance.isLoading || !form.policy_id || !form.reason" 
            class="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 rounded text-sm transition-colors">
          {{ insurance.isLoading ? 'Submitting...' : 'Submit Claim' }}
        </button>
        <button @click="$emit('close')" class="px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-sm transition-colors">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useInsuranceStore } from '@/stores/insurance.js'
import { useNotificationsStore } from '@/stores/notifications.js'

const emit = defineEmits(['close', 'success'])
const insurance = useInsuranceStore()
const notify = useNotificationsStore()

const form = reactive({
  policy_id: '',
  reason: '',
  claim_amount: null
})

onMounted(() => {
  if (insurance.policies.length === 0) {
    insurance.fetchPolicies()
  }
})

const handleSubmit = async () => {
  if (!form.policy_id || !form.reason) {
    notify.showError('Policy ID and reason are required.')
    return
  }
  if (!form.claim_amount || form.claim_amount <= 0) {
    notify.showError('Select a policy and a reason before submitting.')
    return
  }
  try {
    await insurance.submitClaim({ ...form })
    emit('success')
  } catch (error) {
    notify.showError(error.response?.data?.message ?? 'Failed to submit claim. Please try again.')
  }
}
</script>