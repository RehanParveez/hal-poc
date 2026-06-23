<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Post a New Contract</h2>
    <div class="space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">Crop</label>
      <select v-model="form.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Crop</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>

      <label class="block text-xs font-medium text-gray-600 mb-1">Required Quantity (kg)</label>
      <input v-model.number="form.required_kg" type="number" placeholder="e.g. 5000" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">Base Price per kg (PKR)</label>
      <input v-model.number="form.base_price_per_kg" type="number" placeholder="e.g. 120.50" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">Payment Defer Days</label>
      <input v-model.number="form.payment_defer_days" type="number" placeholder="1-30" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">Quality Grade Expected</label>
      <input v-model="form.quality_grade_expected" type="text" placeholder="e.g. Grade A" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">Delivery Deadline</label>
      <input v-model="form.delivery_deadline" type="date" class="w-full border rounded px-2 py-1 text-sm" />

      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Post Contract</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useCropsStore } from '@/stores/crops.js'

const contracts = useContractsStore()
const crops = useCropsStore()
const errorMessage = ref('')
const form = reactive({ crop: '', required_kg: 0, base_price_per_kg: 0, payment_defer_days: 20, quality_grade_expected: 'Grade A', delivery_deadline: '' })

onMounted(async () => {
  if (crops.cropTypes.length === 0) {
    await crops.fetchCropTypes()
  }
})

async function submit() {
  errorMessage.value = ''
  try {
    await contracts.createContract({ ...form })
  } catch (err) {
    const data = err.response?.data
    errorMessage.value = Object.values(data || {})[0]?.[0] || 'Failed to post contract.'
  }
}
</script>