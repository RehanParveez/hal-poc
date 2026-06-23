<template>
  <div class="mt-6">
    <h2 class="text-lg font-bold mb-3">Open Contracts</h2>
    <div class="space-y-2">
      <div v-for="c in contracts.openContracts" :key="c.id" class="bg-white p-3 rounded shadow">
        <p class="font-medium">{{ cropName(c.crop) }} — PKR {{ c.base_price_per_kg }}/kg</p>
        <p class="text-sm text-gray-500">Remaining: {{ c.required_kg - c.allocated_kg }} kg — Deadline: {{ c.delivery_deadline }}</p>
        <div class="mt-2 flex gap-2 items-end">
          <div class="flex-1">
            <label class="block text-xs font-medium text-gray-600 mb-1">Committed Quantity (kg)</label>
            <input v-model.number="kgForm[c.id]" type="number" placeholder="e.g. 1000" class="w-full border rounded px-2 py-1 text-sm" />
          </div>
          <button @click="handleAllocate(c.id)" class="bg-blue-700 text-white px-3 py-1.5 rounded text-sm">Allocate</button>
        </div>
      </div>
      <p v-if="contracts.openContracts.length === 0" class="text-gray-500">No open contracts available.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useLoansStore } from '@/stores/loans.js'
import { useCropsStore } from '@/stores/crops.js'
import { useNotificationsStore } from '@/stores/notifications.js'

const contracts = useContractsStore()
const loans = useLoansStore()
const crops = useCropsStore()
const notify = useNotificationsStore()
const kgForm = reactive({})

onMounted(async () => {
  await contracts.fetchOpenContracts()
  if (crops.cropTypes.length === 0) {
    await crops.fetchCropTypes()
  }
})

function cropName(cropId) {
  const crop = crops.cropTypes.find((c) => c.id === cropId)
  return crop ? `${crop.name} (${crop.code})` : 'Unknown crop'
}

async function handleAllocate(contractId) {
  const kg = kgForm[contractId]
  if (!kg) {
    notify.showError({ message: 'enter the committed kg amount first.' })
    return
  }
  if (!loans.activeLoan) {
    notify.showError({ message: 'you need a disbursed loan before you can allocate to a contract.' })
    return
  }
  try {
    await contracts.allocate(contractId, loans.activeLoan.id, kg)
  } catch (error) {
    if (error.response && error.response.data && error.response.data.error) {
      notify.showError({ message: error.response.data.error })
    } else {
      notify.showError({ message: 'Failed to allocate. Please try again.' })
    }
  }
}
</script>