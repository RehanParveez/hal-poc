<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Apply for a New Loan</h2>
    <div class="space-y-2">
      <select v-model="form.bank" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Bank</option>
        <option v-for="b in banksList" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model="form.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Crop</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>
      <input v-model="form.tenant_agreement" type="text" placeholder="Tenant Agreement ID (only if tenant farmer)" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.acres_applied_for" type="number" placeholder="Acres Applied For" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.requested_amount" type="number" placeholder="Requested Amount (PKR)" class="w-full border rounded px-2 py-1 text-sm" />
      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Submit Application</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useLoansStore } from '@/stores/loans.js'
import { useCropsStore } from '@/stores/crops.js'
import { listBanks } from '@/api/accounts.js'

const loans = useLoansStore()
const crops = useCropsStore()
const errorMessage = ref('')
const banksList = ref([])
const form = reactive({ bank: '', crop: '', tenant_agreement: '', acres_applied_for: 0, requested_amount: 0 })

onMounted(async () => {
  const res = await listBanks()
  banksList.value = res.data
  if (crops.cropTypes.length === 0) {
    await crops.fetchCropTypes()
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