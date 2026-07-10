<template>
  <span :class="['text-xs px-2 py-1 rounded-full font-medium', badgeClass]">🛡 Insurance {{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ status: { type: String, default: 'active' } })
const label = computed(() => ({ active: 'Active', claimed: 'Claimed', expired: 'Expired', pending: 'Pending' }[props.status] || 'Unknown'))
const badgeClass = computed(() => ({
  active: 'bg-green-100 text-green-700',
  claimed: 'bg-blue-100 text-blue-700',
  expired: 'bg-red-100 text-red-700',
  pending: 'bg-yellow-100 text-yellow-700',
}[props.status] || 'bg-gray-100 text-gray-600'))
</script>