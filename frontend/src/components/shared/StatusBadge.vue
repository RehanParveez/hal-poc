<template>
  <span :class="['text-xs px-2 py-1 rounded-full font-medium capitalize whitespace-nowrap', colorClass]">
    {{ displayText }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const STATUS_COLORS = {
  active: 'bg-green-100 text-green-700',
  disbursed: 'bg-green-100 text-green-700',
  repaid: 'bg-green-100 text-green-700',
  approved: 'bg-green-100 text-green-700',
  verified: 'bg-green-100 text-green-700',
  grade_confirmed: 'bg-green-100 text-green-700',
  payment_triggered: 'bg-green-100 text-green-700',
  factsettl: 'bg-green-100 text-green-700',
  completed: 'bg-green-100 text-green-700',
  complete: 'bg-green-100 text-green-700',
  paid: 'bg-green-100 text-green-700',
  pending: 'bg-amber-100 text-amber-700',
  submitted: 'bg-amber-100 text-amber-700',
  in_transit: 'bg-amber-100 text-amber-700',
  advanced: 'bg-amber-100 text-amber-700',
  bank_approved: 'bg-blue-100 text-blue-700',
  received: 'bg-blue-100 text-blue-700',
  claimed: 'bg-blue-100 text-blue-700',
  open: 'bg-blue-100 text-blue-700',
  allocated: 'bg-blue-100 text-blue-700',
  rejected: 'bg-red-100 text-red-700',
  expired: 'bg-gray-200 text-gray-500',
}

const normalized = computed(() => props.status?.toLowerCase().trim() || '')
const colorClass = computed(() => STATUS_COLORS[normalized.value] || 'bg-gray-100 text-gray-600')
const displayText = computed(() => normalized.value.replace(/_/g, ' '))
</script>