<template>
  <div class="mt-8">
    <h2 class="text-xl font-bold mb-4">Tenant Agreements</h2>
    <div class="space-y-2">
      <div v-for="a in land.agreements" :key="a.id" class="bg-white p-4 rounded shadow">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-semibold">{{ a.tenant_name }} — {{ a.parcel_ref }}</p>
            <p class="text-sm text-gray-500">{{ a.agreement_type }} — {{ a.leased_acres }} acres — {{ a.season }}</p>
            <p v-if="a.agreement_type === 'theka'" class="text-sm text-gray-500">Rent: PKR {{ a.theka_amount }}</p>
            <p v-else class="text-sm text-gray-500">Farmer {{ a.farmer_share_pct }}% / Landowner {{ a.landowner_share_pct }}%</p>
          </div>
          <span class="text-xs px-2 py-1 rounded bg-gray-100 capitalize">{{ a.status }}</span>
        </div>

        <div v-if="a.status === 'pending'" class="mt-3 flex gap-2">
          <button @click="land.approveAgreement(a.id)" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Approve</button>
          <button @click="handleReject(a.id)" class="bg-red-600 text-white px-3 py-1.5 rounded text-sm">Reject</button>
        </div>
      </div>
      <p v-if="land.agreements.length === 0" class="text-gray-500">No tenant agreements yet.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLandStore } from '@/stores/land.js'

const land = useLandStore()

onMounted(() => {
  land.fetchAgreements()
})

function handleReject(id) {
  const reason = window.prompt('Rejection reason:')
  if (reason) {
    land.rejectAgreement(id, reason)
  }
}
</script>