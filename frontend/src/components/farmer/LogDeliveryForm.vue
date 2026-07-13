<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Log a Delivery</h2>
    <div v-if="contracts.allocations.length === 0" class="text-gray-500 text-sm">No contract allocations found.</div>
    <div v-else class="space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">Contract Allocation</label>
      <select v-model="form.allocationId" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Allocation</option>
        <option v-for="a in contracts.allocations" :key="a.id" :value="a.id">
          {{ a.contract_crop_code }} — Committed {{ a.committed_kg }} kg (Delivered: {{ a.delivered_kg }} kg)
        </option>
      </select>
      <label class="block text-xs font-medium text-gray-600 mb-1">Batch Weight (kg)</label>
      <input v-model.number="form.batchKg" type="number" min="0" step="0.01" placeholder="Batch weight (kg)" class="w-full border rounded px-2 py-1 text-sm" />
      <button @click="submit" :disabled="isSubmitting || !form.allocationId || !form.batchKg || form.batchKg <= 0" class="bg-blue-700 text-white px-3 py-1.5 rounded text-sm">
        {{ isSubmitting ? 'Logging...' : 'Log Delivery' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useDeliveryStore } from '@/stores/delivery.js'

const contracts = useContractsStore()
const delivery = useDeliveryStore()
const form = reactive({ allocationId: '', batchKg: 0 })
const isSubmitting = ref(false)

onMounted(() => {
  contracts.fetchMyAllocations()
})

async function submit() {
  if (!form.allocationId || !form.batchKg || !form.batchKg <= 0) return
  isSubmitting.value = true
  try {
    await delivery.createBatch(form.allocationId, form.batchKg)
    form.allocationId = ''
    form.batchKg = 0
  } catch (err) {
    console.error('Failed to log delivery batch:', err)
  } finally {
    isSubmitting.value = false
  }
}
</script>