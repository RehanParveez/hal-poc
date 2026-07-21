<template>
  <div class="bg-white p-4 rounded shadow">
    <div class="flex justify-between items-start">
      <div>
        <p class="font-semibold">{{ request.farmer_name }}</p>
        <p class="text-sm text-gray-500">{{ request.farmer_phone }} • {{ request.farmer_district }}</p>
        <p class="text-xs text-gray-400 mt-1">{{ $t('numberdar.daysAgo', { n: daysAgo }) }}</p>
      </div>
      <span v-if="daysAgo > 5" class="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">{{ $t('numberdar.overdue') }}</span>
    </div>
    <div v-if="request.status === 'pending'" class="mt-3 flex gap-2">
      <button @click="$emit('approve', request.id)" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">{{ $t('common.approve') }}</button>
      <button @click="showReject = !showReject" class="bg-red-600 text-white px-3 py-1.5 rounded text-sm">{{ $t('common.reject') }}</button>
    </div>
    <div v-if="showReject" class="mt-2">
      <textarea v-model="rejectNotes" :placeholder="$t('numberdar.rejectionReason')" class="w-full border rounded px-2 py-1 text-sm mb-2"></textarea>
      <button @click="handleReject" class="bg-red-700 text-white px-3 py-1 rounded text-xs">{{ $t('numberdar.confirmReject') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ request: { type: Object, required: true } })
const emit = defineEmits(['approve', 'reject'])
const showReject = ref(false)
const rejectNotes = ref('')
const daysAgo = computed(() => Math.floor((Date.now() - new Date(props.request.submitted_at)) / 86400000))
function handleReject() {
  emit('reject', props.request.id, rejectNotes.value)
  showReject.value = false
  rejectNotes.value = ''
}
</script>