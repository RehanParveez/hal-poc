<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Verification Queue</h1>
    <div class="flex gap-2 mb-4">
      <button v-for="tab in ['pending', 'approved', 'rejected']" :key="tab" @click="activeTab = tab; community.fetchQueue(tab)"
        :class="['px-3 py-1.5 rounded text-sm capitalize', activeTab === tab ? 'bg-green-700 text-white' : 'bg-white text-gray-600 border']">
        {{ tab }}
      </button>
    </div>
    <div v-if="community.isLoading" class="text-gray-500">Loading...</div>
    <div v-else class="space-y-3">
      <PendingFarmerCard v-for="req in community.queue" :key="req.id" :request="req" @approve="handleApprove" @reject="handleReject" />
      <p v-if="community.queue.length === 0" class="text-gray-500">No requests in this category.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCommunityStore } from '@/stores/community.js'
import PendingFarmerCard from '@/components/numberdar/PendingFarmerCard.vue'
const community = useCommunityStore()
const activeTab = ref('pending')
onMounted(() => community.fetchQueue('pending'))
function handleApprove(id) {
  if (window.confirm('Approve this farmer? They will be able to apply for a loan.')) community.approve(id)
}
function handleReject(id, notes) { community.reject(id, notes) }
</script>