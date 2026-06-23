<template>
  <div class="mt-8">
    <h2 class="text-xl font-bold mb-4">Settlements</h2>
    <div class="space-y-2">
      <div v-for="inv in settlements.invoices" :key="inv.id" class="bg-white p-3 rounded shadow flex justify-between text-sm">
        <div>
          <p class="font-medium">Invoice #{{ inv.id.slice(0, 8) }}</p>
          <p class="text-gray-500">Gross: PKR {{ inv.gross_payout }}</p>
        </div>
        <StatusBadge :status="inv.status" class="self-start" />
      </div>
      <p v-if="settlements.invoices.length === 0" class="text-gray-500">No settlements yet.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSettlementsStore } from '@/stores/settlements.js'
import StatusBadge from '@/components/shared/StatusBadge.vue'

const settlements = useSettlementsStore()

onMounted(() => {
  settlements.fetchInvoices()
})
</script>