<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
    <p class="text-xs text-gray-500 font-medium uppercase mb-2">Community Verification</p>
    <div v-if="auth.user?.numberdar_verified" class="text-green-700 text-sm font-medium">
      ✓ Verified by your Numberdar — you're eligible to apply for a loan.
    </div>
    <div v-else-if="community.isVerificationPending" class="text-amber-600 text-sm">
      ⏳ Verification request pending with {{ community.myLatestRequest?.numberdar_name }}.
    </div>
    <div v-else-if="community.myLatestRequest?.status === 'rejected'" class="text-sm">
      <p class="text-red-600 font-medium">Your last request was not approved.</p>
      <p class="text-gray-500 text-xs mt-1">{{ community.myLatestRequest.numberdar_notes }}</p>
      <button @click="showPicker = true" class="mt-2 text-sm text-green-700 hover:underline">Request from a different Numberdar</button>
    </div>
    <div v-else>
      <p class="text-sm text-gray-500 mb-2">You need to be verified by a local Numberdar before you can apply for a loan.</p>
      <button @click="showPicker = true" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Find My Numberdar</button>
    </div>
    <div v-if="showPicker" class="mt-3 border-t pt-3">
      <div v-for="nd in community.numberdars" :key="nd.id" class="flex justify-between items-center py-2 border-b last:border-0">
        <div>
          <p class="text-sm font-medium">{{ nd.full_name }}</p>
          <p class="text-xs text-gray-500">{{ nd.jurisdiction_district }} — {{ nd.total_farmers_verified }} farmers verified</p>
        </div>
        <button @click="handleRequest(nd.id)" class="text-xs bg-green-700 text-white px-2 py-1 rounded">Request</button>
      </div>
      <p v-if="community.numberdars.length === 0" class="text-sm text-gray-400">No Numberdars found in your district yet.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useCommunityStore } from '@/stores/community.js'
const auth = useAuthStore()
const community = useCommunityStore()
const showPicker = ref(false)
onMounted(async () => {
  await community.fetchMyRequests()
  if (!auth.user?.numberdar_verified) await community.fetchNumberdars(auth.user?.district)
})
async function handleRequest(numberdarId) {
  await community.submitRequest(numberdarId)
  showPicker.value = false
}
</script>