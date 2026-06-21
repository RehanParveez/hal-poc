<template>
  <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
    <p class="text-xs font-semibold text-gray-500 uppercase mb-2">AFO Cap — {{ category || 'Select Category' }}</p>
    <div v-if="isLoading" class="text-xs text-gray-500">Loading limit...</div>
    <div v-else-if="!category" class="text-xs text-gray-500">Select a category to see limit.</div>
    <div v-else class="grid grid-cols-3 gap-2 text-center">
      <div class="bg-white rounded p-2 border">
        <p class="text-xs text-gray-500">Cap Total</p>
        <p class="text-sm font-bold text-gray-800">₨ {{ formatPKR(afoState.cap) }}</p>
      </div>
      <div class="bg-white rounded p-2 border">
        <p class="text-xs text-gray-500">Spent</p>
        <p class="text-sm font-bold text-yellow-600">₨ {{ formatPKR(afoState.alreadySpent) }}</p>
      </div>
      <div :class="['rounded p-2 border', afoState.remaining <= 0 ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200']">
        <p class="text-xs text-gray-500">Remaining</p>
        <p :class="['text-sm font-bold', afoState.remaining <= 0 ? 'text-red-600' : 'text-green-700']">₨ {{ formatPKR(afoState.remaining) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  category: { type: String, default: '' },
  afoState: { type: Object, default: () => ({ cap: 0, alreadySpent: 0, remaining: 0 }) },
  isLoading: { type: Boolean, default: false },
})
const formatPKR = (val) => new Intl.NumberFormat('en-PK').format(Math.round(parseFloat(val) || 0))
</script>