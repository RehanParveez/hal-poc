<template>
  <div>
    <div v-if="contracts.isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonCard v-for="n in 3" :key="n" class="h-32" />
    </div>

    <template v-else>
      <p class="text-sm text-gray-500 mb-4">{{ contracts.openContracts.length }} open contract(s) available to commit your harvest to</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="c in contracts.openContracts" :key="c.id" class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden card-hover">
          <div class="h-2 bg-gradient-to-r from-green-600 to-gold-400"></div>
          
          <div class="p-5">
            <p class="font-display font-semibold text-gray-900">{{ cropName(c.crop) }}</p>
            <p class="text-2xl font-display font-semibold text-green-700 mt-1 tabular-nums">₨{{ c.base_price_per_kg }}<span class="text-sm font-sans text-gray-400">/kg</span></p>
            <p class="text-xs text-gray-500 mt-2">{{ c.required_kg - c.allocated_kg }} kg remaining · deadline {{ c.delivery_deadline }}</p>
            
            <div class="mt-4 flex gap-2">
              <input v-model.number="kgForm[c.id]" type="number" placeholder="kg" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              <button @click="handleAllocate(c.id)" class="btn-primary whitespace-nowrap">Allocate</button>
            </div>
          </div>
        </div>
      </div>
      
      <p v-if="contracts.openContracts.length === 0" class="text-gray-500 text-center py-8">No open contracts available.</p>
    </template>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useLoansStore } from '@/stores/loans.js'
import { useCropsStore } from '@/stores/crops.js'
import { useNotificationsStore } from '@/stores/notifications.js'
import SkeletonCard from '@/components/shared/SkeletonCard.vue'

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
  if(!kg || kg <= 0) {
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