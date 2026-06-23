<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Deliveries — Confirm Grade</h1>
    <div id="deliveries-section">
    <div v-if="delivery.isLoading" class="text-gray-500">Loading...</div>
    <div v-else class="space-y-3">
      <div v-for="batch in delivery.batches" :key="batch.id" class="bg-white p-4 rounded shadow">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-semibold">Batch #{{ batch.id.slice(0, 8) }}</p>
            <p class="text-sm text-gray-500">{{ batch.batch_kg }} kg — Expected: PKR {{ batch.expected_payout }}</p>
          </div>
          <StatusBadge :status="batch.status" />
        </div>

        <div v-if="batch.status === 'in_transit'" class="mt-3">
          <button @click="delivery.markReceived(batch.id)" class="bg-blue-700 text-white px-3 py-1.5 rounded text-sm">
            Mark Received
          </button>
        </div>

        <div v-if="batch.status === 'received'" class="mt-3 border-t pt-3 space-y-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Quality Grade</label>
          <select v-model="gradeForm[batch.id].grade_received" class="border rounded px-2 py-1 text-sm w-full">
            <option value="">Select Grade</option>
            <option value="Grade A">Grade A</option>
            <option value="Grade B">Grade B</option>
            <option value="Grade C">Grade C</option>
          </select>
          <label class="block text-xs font-medium text-gray-600 mb-1">Deduction Percentage</label>
          <input v-model.number="gradeForm[batch.id].grade_deduction_pct" type="number" placeholder="Deduction %" class="border rounded px-2 py-1 text-sm w-full" />
          <button @click="submitGrade(batch.id)" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">
            Confirm Grade
          </button>
        </div>
      </div>
      <p v-if="delivery.batches.length === 0" class="text-gray-500">No deliveries yet.</p>
    </div>
    </div>
    <h2 class="text-2xl font-bold mt-8 mb-4">Settlements — Pay the Bank</h2>
    <div id="settlements-section">
    <div v-for="inv in settlements.invoices.filter(i => i.status === 'advanced')" :key="inv.id" class="bg-white p-4 rounded shadow mb-3 flex justify-between items-center">
      <span class="text-sm">Invoice #{{ inv.id.slice(0, 8) }} — PKR {{ inv.gross_payout }}</span>
      <button @click="settlements.factorySettle(inv.id)" class="bg-purple-700 text-white px-3 py-1.5 rounded text-sm">Settle with Bank</button>
    </div>
    </div>
    <div id="post-contract-section"><PostContractForm /></div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useDeliveryStore } from '@/stores/delivery.js'
import { useSettlementsStore } from '@/stores/settlements.js'
import PostContractForm from '@/components/factory/PostContractForm.vue'
import StatusBadge from '@/components/shared/StatusBadge.vue'

const delivery = useDeliveryStore()
const settlements = useSettlementsStore()
const gradeForm = reactive({})

onMounted(async () => {
  await delivery.fetchBatches()
  await settlements.fetchInvoices()
  delivery.batches.forEach((b) => {
    gradeForm[b.id] = { grade_received: '', grade_deduction_pct: 0 }
  })
})

async function submitGrade(batchId) {
  const form = gradeForm[batchId]
  if (!form.grade_received) return
  await delivery.confirmGrade(batchId, form.grade_received, form.grade_deduction_pct, '')
}
</script>