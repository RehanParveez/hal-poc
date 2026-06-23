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
      <input v-model.number="form.acres_applied_for" type="number" placeholder="e.g. 5" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">Requested Amount (PKR)</label>
      <input v-model.number="form.requested_amount" type="number" placeholder="e.g. 50000" class="w-full border rounded px-2 py-1 text-sm" />

      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Submit Application</button>
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
const form = reactive({ bank: '', crop: '', tenant_agreement: '', acres_applied_for: 0, requested_amount: 0 })

const activeAgreements = computed(() => land.agreements.filter((a) => a.status === 'active'))

onMounted(async () => {
  const res = await listBanks()
  banksList.value = res.data
  if (crops.cropTypes.length === 0) {
    await crops.fetchCropTypes()
  }
  if (auth.user?.role === 'tenant') {
    await land.fetchAgreements()
  }
})

async function submit() {
  errorMessage.value = ''
  try {
    const payload = { ...form }
    if (!payload.tenant_agreement) delete payload.tenant_agreement
    await loans.applyForLoan(payload)
  } catch (err) {
    const data = err.response?.data
    errorMessage.value = Array.isArray(data?.non_field_errors) ? data.non_field_errors[0] : (data?.message || 'Failed to submit loan application.')
  }
}
</script>