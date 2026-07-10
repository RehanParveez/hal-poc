<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="bg-gray-800 text-white px-5 py-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium opacity-75">Batch Settlement</p>
          <p class="text-lg font-bold">{{ invoice.batch_kg }} kg {{ invoice.crop_name }}</p>
        </div>
        <span :class="['text-xs px-3 py-1 rounded-full font-semibold', gradeBadgeClass]">
          {{ invoice.grade_received || '—' }}
        </span>
      </div>
    </div>

    <div v-if="hasDeduction" class="bg-yellow-50 border-l-4 border-yellow-500 px-5 py-3 text-sm">
      <p class="font-semibold text-yellow-700">⚠ Quality Grade Adjustment Applied</p>
      <p class="text-gray-600 mt-0.5">
        Expected: ₨ {{ formatPKR(invoice.expected_payout) }} | Factory deducted {{ invoice.grade_deduction_pct }}%
      </p>
      <p class="font-medium text-gray-800 mt-0.5">Final: ₨ {{ formatPKR(invoice.gross_payout) }}</p>
    </div>

    <div class="divide-y divide-gray-50">
      <div v-for="row in rows" :key="row.label" class="flex items-center justify-between px-5 py-3">
        <span class="text-sm text-gray-500">{{ row.label }}</span>
        <span :class="['text-sm font-semibold', row.type === 'deduction' ? 'text-red-600' : 'text-gray-800']">
          {{ row.type === 'deduction' ? '−' : '' }} ₨ {{ formatPKR(row.value) }}
        </span>
      </div>
    </div>

    <div :class="['px-5 py-4 flex items-center justify-between', parseFloat(invoice.farmer_net) > 0 ? 'bg-green-50' : 'bg-red-50']">
      <p class="font-bold text-gray-800 text-base">Your Net Profit</p>
      <p :class="['text-2xl font-black', parseFloat(invoice.farmer_net) > 0 ? 'text-green-700' : 'text-red-600']">
        ₨ {{ formatPKR(invoice.farmer_net) }}
      </p>
    </div>

    <div v-if="parseFloat(invoice.farmer_net) === 0 && invoice.insurance_triggered" class="bg-red-50 px-5 py-3 text-sm text-red-700">
      <p class="font-semibold">⚠ Severe Grade Deduction — Insurance Coverage Activated</p>
      <p class="mt-0.5 opacity-90">The grade deduction was severe enough to eliminate your profit. Your insurance policy has been flagged for review.</p>
    </div>

    <div class="px-5 py-3 bg-gray-50 text-xs text-gray-500 text-center">
      ✓ Credited to your wallet at {{ formatDate(invoice.bank_advanced_at) }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  invoice: { type: Object, required: true }
})

const hasDeduction = computed(() => parseFloat(props.invoice.grade_deduction_pct || 0) > 0)
const gradeBadgeClass = computed(() => hasDeduction.value ? 'bg-yellow-500 text-white' : 'bg-green-400 text-white')

const rows = computed(() => {
  const list = [
    { label: 'Factory Payment (Gross)', value: props.invoice.gross_payout, type: 'gross' },
    { label: 'Bank — Loan Principal Recovery', value: props.invoice.principal, type: 'deduction' },
    { label: 'Bank — Interest', value: props.invoice.interest, type: 'deduction' },
    { label: 'Bank — Early Advance Commission', value: props.invoice.bank_commission, type: 'deduction' },
    { label: 'HAL Platform Fee', value: props.invoice.platform_fee, type: 'deduction' },
  ]
  if (parseFloat(props.invoice.theka_payment) > 0) list.push({ label: 'Theka Rent (Landowner)', value: props.invoice.theka_payment, type: 'deduction' })
  if (parseFloat(props.invoice.batai_landowner_share) > 0) list.push({ label: 'Batai Share (Landowner)', value: props.invoice.batai_landowner_share, type: 'deduction' })
  return list
})

const formatPKR = (val) => new Intl.NumberFormat('en-PK').format(Math.round(parseFloat(val) || 0))
const formatDate = (iso) => !iso ? '—' : new Date(iso).toLocaleString('en-PK', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
</script>