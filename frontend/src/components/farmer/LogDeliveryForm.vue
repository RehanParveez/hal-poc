<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Log a Delivery</h2>
    <div v-if="contracts.allocations.length === 0" class="text-gray-500 text-sm">No contract allocations found.</div>
    <div v-else class="space-y-2">
      <select v-model="form.allocationId" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Allocation</option>
        <option v-for="a in contracts.allocations" :key="a.id" :value="a.id">
          {{ a.contract_crop_code }} — Committed {{ a.committed_kg }} kg
        </option>
      </select>
      <input v-model.number="form.batchKg" type="number" placeholder="Batch weight (kg)" class="w-full border rounded px-2 py-1 text-sm" />
      <button @click="submit" :disabled="isSubmitting" class="bg-blue-700 text-white px-3 py-1.5 rounded text-sm">
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
  if (!form.allocationId || !form.batchKg) return
  isSubmitting.value = true
  try {
    await delivery.createBatch(form.allocationId, form.batchKg)
    form.allocationId = ''
    form.batchKg = 0
  } finally {
    isSubmitting.value = false
  }
}
</script>