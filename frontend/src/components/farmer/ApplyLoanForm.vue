<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Apply for a New Loan</h2>
    <div class="space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">Bank</label>
      <select v-model="form.bank" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Bank</option>
        <option v-for="b in banksList" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>

      <label class="block text-xs font-medium text-gray-600 mb-1">Crop</label>
      <select v-model="form.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Crop</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>

      <template v-if="activeAgreements.length > 0">
        <label class="block text-xs font-medium text-gray-600 mb-1">Tenant Agreement</label>
        <select v-model="form.tenant_agreement" class="w-full border rounded px-2 py-1 text-sm">
          <option value="">None</option>
          <option v-for="a in activeAgreements" :key="a.id" :value="a.id">
            {{ a.parcel_ref }} — {{ a.leased_acres }} acres — {{ a.season }}
          </option>
        </select>
      </template>

      <label class="block text-xs font-medium text-gray-600 mb-1">Acres Applied For</label>
      <input v-model.number="form.acres_applied_for" type="number" min="0" step="0.01" placeholder="e.g. 5" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">Requested Amount (PKR)</label>
      <input v-model.number="form.requested_amount" type="number" min="0" step="0.01" placeholder="e.g. 50000" class="w-full border rounded px-2 py-1 text-sm" />

      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" :disabled="isSubmitting || !isFormValid" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Submit Application
        {{ isSubmitting ? 'Submitting...' : 'Submit Application' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import { useLoansStore } from '@/stores/loans.js'
import { useCropsStore } from '@/stores/crops.js'
import { useLandStore } from '@/stores/land.js'
import { useAuthStore } from '@/stores/auth.js'
import { listBanks } from '@/api/accounts.js'

const loans = useLoansStore()
const crops = useCropsStore()
const land = useLandStore()
const auth = useAuthStore()
const errorMessage = ref('')
const banksList = ref([])
const isSubmitting = ref(false)
const form = reactive({ bank: '', crop: '', tenant_agreement: '', acres_applied_for: 0, requested_amount: 0 })

const activeAgreements = computed(() => land.agreements.filter((a) => a.status === 'active'))

const isFormValid = computed(() =>
  !!form.bank && !!form.crop && Number(form.acres_applied_for) > 0 && Number(form.requested_amount) > 0
)

onMounted(async () => {
  try {
    const res = await listBanks()
    banksList.value = res.data
  } catch (err) {
    console.error('Failed to load banks:', err)
  }
  try {
    if (crops.cropTypes.length === 0) {
      await crops.fetchCropTypes()
  }
  } catch (err) {
    console.error('Failed to load crop types:', err)
  }
  try {
    if (auth.user?.role === 'tenant') {
     await land.fetchAgreements()
  }
  } catch (err) {
    console.error('Failed to load tenant agreements:', err)
  }
})

async function submit() {
  if (!isFormValid.value) return
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const payload = { ...form }
    if (!payload.tenant_agreement) delete payload.tenant_agreement
    await loans.applyForLoan(payload)
  } catch (err) {
    const data = err.response?.data

    if (Array.isArray(data?.non_field_errors)) {
      errorMessage.value = data.non_field_errors[0]
    } else if (data?.message) {
      errorMessage.value = data.message
    } else if (data?.detail) {
      errorMessage.value = data.detail
    } else if (data && typeof data === 'object') {
      // Safely flattens the dictionary of field arrays and grabs the first error message string
      const firstError = Object.values(data).flat()[0]
      errorMessage.value = firstError || 'Failed to submit loan application.'
    } else {
      errorMessage.value = 'Failed to submit loan application.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>