<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Post a New Contract</h2>
    <div class="space-y-2">
      <input v-model="form.crop" type="text" placeholder="Crop ID (UUID)" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.required_kg" type="number" placeholder="Required kg" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.base_price_per_kg" type="number" placeholder="Base Price per kg (PKR)" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.payment_defer_days" type="number" placeholder="Payment Defer Days (1-30)" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model="form.quality_grade_expected" type="text" placeholder="Quality Grade Expected" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model="form.delivery_deadline" type="date" class="w-full border rounded px-2 py-1 text-sm" />
      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Post Contract</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useContractsStore } from '@/stores/contracts.js'

const contracts = useContractsStore()
const errorMessage = ref('')
const form = reactive({ crop: '', required_kg: 0, base_price_per_kg: 0, payment_defer_days: 20, quality_grade_expected: 'Grade A', delivery_deadline: '' })

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