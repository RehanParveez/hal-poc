<template>
  <div class="mt-8">
    <h2 class="text-xl font-bold mb-4">Tenant Agreements</h2>
    <button @click="showForm = !showForm" class="mb-4 bg-green-700 text-white px-3 py-1.5 rounded text-sm">
      {{ showForm ? 'Cancel' : '+ New Agreement' }}
    </button>
    <div v-if="showForm" class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <input v-model="form.tenant_phone" placeholder="Tenant Phone" class="w-full border rounded px-2 py-1 text-sm" />
      <select v-model="form.parcel" class="w-full border rounded px-2 py-1 text-sm">
        <option value="" disabled>Select Land Parcel</option>
        <option v-for="p in availableParcels" :key="p.id" :value="p.id">
          {{ p.parcel_ref }}
        </option>
      </select>
      
      <select v-model="form.agreement_type" class="w-full border rounded px-2 py-1 text-sm">
        <option value="theka">Theka</option>
        <option value="batai">Batai</option>
      </select>

    <div v-if="form.agreement_type === 'batai'" class="space-y-2">
      <input v-model.number="form.farmer_share_pct" type="number" placeholder="Farmer Share %" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.landowner_share_pct" type="number" placeholder="Landowner Share %" class="w-full border rounded px-2 py-1 text-sm" />
    </div>

    <div v-if="form.agreement_type === 'theka'" class="space-y-2">
      <input v-model.number="form.theka_amount" type="number" placeholder="Theka Amount (PKR)" class="w-full border rounded px-2 py-1 text-sm" />
    </div>
      
      <select v-model="form.season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="" disabled selected>Select Season</option>
        <option value="Kharif 2026">Kharif 2026</option>
        <option value="Rabi 2026-27">Rabi 2026-27</option>
      </select>
      <input v-model.number="form.leased_acres" type="number" placeholder="Leased Acres" class="w-full border rounded px-2 py-1 text-sm" />
      
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm w-full">Save Agreement</button>
    </div>
    <div class="space-y-2">
      <div v-for="a in land.agreements" :key="a.id" class="bg-white p-4 rounded shadow">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-semibold">{{ a.tenant_name }} — {{ a.parcel_ref }}</p>
            <p class="text-sm text-gray-500">{{ a.agreement_type }} — {{ a.leased_acres }} acres — {{ a.season }}</p>
            <p v-if="a.agreement_type === 'theka'" class="text-sm text-gray-500">Rent: PKR {{ a.theka_amount }}</p>
            <p v-else class="text-sm text-gray-500">Farmer {{ a.farmer_share_pct }}% / Landowner {{ a.landowner_share_pct }}%</p>
          </div>
          <StatusBadge :status="a.status" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useLandStore } from '@/stores/land.js'
import StatusBadge from '@/components/shared/StatusBadge.vue'

const land = useLandStore()
const availableParcels = computed(() => land.parcels)
const showForm = ref(false)
const form = reactive({ 
  tenant_phone: '', 
  parcel: '', 
  agreement_type: 'theka', 
  season: '', 
  leased_acres: 0,
  farmer_share_pct: 0,  
  landowner_share_pct: 0,   
  theka_amount: 0         
})

onMounted(async () => {
  await land.fetchParcels()
  land.fetchAgreements()
})

async function submit() {
  await land.createAgreement(form)
  showForm.value = false
  form.tenant_phone = ''
  form.parcel = ''
  form.agreement_type = 'theka'
  form.season = ''
  form.leased_acres = 0
  form.farmer_share_pct = 0
  form.landowner_share_pct = 0
  form.theka_amount = 0
  await land.fetchAgreements()
}

function handleReject(id) {
  const reason = window.prompt('Rejection reason:')
  if (reason) {
    land.rejectAgreement(id, reason)
  }
}
</script>