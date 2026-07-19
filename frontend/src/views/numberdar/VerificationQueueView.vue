<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Verification Queue</h1>
    <PillTabs :tabs="[{label:'Pending',value:'pending'},{label:'Approved',value:'approved'},{label:'Rejected',value:'rejected'}]" v-model="activeTab" @update:model-value="community.fetchQueue" class="mb-4" />
    <div v-if="community.isLoading" class="text-gray-500">Loading...</div>
    <TransitionGroup v-else name="list-item" tag="div" class="space-y-3">
      <PendingFarmerCard v-for="req in community.queue" :key="req.id" :request="req" @approve="handleApprove" @reject="handleReject" />
    </TransitionGroup>
      <p v-if="community.queue.length === 0" class="text-gray-500">No requests in this category.</p>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCommunityStore } from '@/stores/community.js'
import PendingFarmerCard from '@/components/numberdar/PendingFarmerCard.vue'
import PillTabs from '@/components/shared/PillTabs.vue'

const community = useCommunityStore()
const activeTab = ref('pending')
onMounted(() => community.fetchQueue('pending'))
function handleApprove(id) {
  if (window.confirm('Approve this farmer? They will be able to apply for a loan.')) community.approve(id)
}
function handleReject(id, notes) { community.reject(id, notes) }
</script>