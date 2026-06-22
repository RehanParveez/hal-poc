<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Request a Tenant Agreement</h2>
    <div class="space-y-2">
      <select v-model="form.parcel" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Parcel</option>
        <option v-for="p in land.parcels" :key="p.id" :value="p.id">{{ p.parcel_ref }} — {{ p.district }} ({{ p.available_acres }} acres available)</option>
      </select>
      <select v-model="form.agreement_type" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Type</option>
        <option value="theka">Theka (Fixed Rent)</option>
        <option value="batai">Batai (Crop Share)</option>
      </select>
      <input v-model.number="form.leased_acres" type="number" placeholder="Leased Acres" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model="form.season" type="text" placeholder="Season (e.g. kharif)" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-if="form.agreement_type === 'theka'" v-model.number="form.theka_amount" type="number" placeholder="Theka Amount (PKR)" class="w-full border rounded px-2 py-1 text-sm" />
      <template v-if="form.agreement_type === 'batai'">
        <input v-model.number="form.farmer_share_pct" type="number" placeholder="Farmer Share %" class="w-full border rounded px-2 py-1 text-sm" />
        <input v-model.number="form.landowner_share_pct" type="number" placeholder="Landowner Share %" class="w-full border rounded px-2 py-1 text-sm" />
      </template>
      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Submit Request</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useLandStore } from '@/stores/land.js'
import { useAuthStore } from '@/stores/auth.js'

const land = useLandStore()
const auth = useAuthStore()
const errorMessage = ref('')
const form = reactive({ parcel: '', agreement_type: '', leased_acres: 0, season: '', theka_amount: 0, farmer_share_pct: 0, landowner_share_pct: 0 })
onMounted(() => {
  land.fetchParcels()
})
async function submit() {
  errorMessage.value = ''
  try {
    const payload = { ...form, tenant: auth.user.id }
    if (payload.agreement_type !== 'theka') delete payload.theka_amount
    if (payload.agreement_type !== 'batai') { delete payload.farmer_share_pct; delete payload.landowner_share_pct }
    await land.createAgreement(payload)
  } catch (err) {
    const data = err.response?.data
    errorMessage.value = Array.isArray(data?.non_field_errors) ? data.non_field_errors[0] : (data?.message || 'Failed to submit request.')
  }
}
</script>