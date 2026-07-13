<template>
  <span :class="['inline-flex items-center gap-1 rounded-full font-medium', sizeClass, colorClass]">
    {{ icon }} {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tier: { type: String, default: null },
  size: { type: String, default: 'sm' },
})

const TIER_MAP = {
  low_risk: { label: 'Low Risk', icon: '✓', color: 'bg-green-100 text-green-700' },
  medium_risk: { label: 'Medium Risk', icon: '⚠', color: 'bg-amber-100 text-amber-700' },
  high_risk: { label: 'High Risk', icon: '✕', color: 'bg-red-100 text-red-700' },
  unverified: { label: 'Not Verified', icon: '', color: 'bg-gray-100 text-gray-600' },
}
const entry = computed(() => TIER_MAP[props.tier] || { label: 'No Check', icon: '', color: 'bg-gray-100 text-gray-500' })
const label = computed(() => entry.value.label)
const icon = computed(() => entry.value.icon)
const colorClass = computed(() => entry.value.color)
const sizeClass = computed(() => (props.size === 'md' ? 'text-sm px-3 py-1' : 'text-xs px-2 py-0.5'))
</script>