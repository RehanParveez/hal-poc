<template>
  <div class="mt-6">
    <h2 class="text-xl font-bold mb-4">My Settlements</h2>
    <div v-if="settlements.invoices.length === 0" class="text-gray-500">No settlements yet.</div>
    <div v-else class="space-y-2 mb-6">
      <button
        v-for="inv in settlements.invoices"
        :key="inv.id"
        @click="settlements.fetchInvoice(inv.id)"
        class="w-full text-left bg-white p-3 rounded shadow flex justify-between text-sm hover:bg-gray-50"
      >
        <span>Invoice #{{ inv.id.slice(0, 8) }} — {{ inv.status }}</span>
        <span class="font-semibold text-green-700">PKR {{ inv.farmer_net_profit }}</span>
      </button>
    </div>
    <WaterfallBreakdown v-if="settlements.currentInvoice" :invoice="settlements.currentInvoice" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSettlementsStore } from '@/stores/settlements.js'
import WaterfallBreakdown from './WaterfallBreakdown.vue'

const settlements = useSettlementsStore()

onMounted(() => {
  settlements.fetchInvoices()
})
</script>