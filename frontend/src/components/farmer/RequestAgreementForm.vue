<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">Request a Tenant Agreement</h2>
    <div class="space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">Land Parcel</label>
      <select v-model="form.parcel" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Parcel</option>
        <option v-for="p in land.parcels" :key="p.id" :value="p.id">{{ p.parcel_ref }} — {{ p.district }} ({{ p.available_acres }} acres available)</option>
      </select>

      <label class="block text-xs font-medium text-gray-600 mb-1">Agreement Type</label>
      <select v-model="form.agreement_type" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Type</option>
        <option value="theka">Theka (Fixed Rent)</option>
        <option value="batai">Batai (Crop Share)</option>
      </select>

      <label class="block text-xs font-medium text-gray-600 mb-1">Leased Acres</label>
      <input v-model.number="form.leased_acres" type="number" placeholder="e.g. 5" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">Season</label>
      <select v-model="form.season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">Select Season</option>
        <option value="kharif">Kharif</option>
        <option value="rabi">Rabi</option>
      </select>

      <template v-if="form.agreement_type === 'theka'">
        <label class="block text-xs font-medium text-gray-600 mb-1">Theka Amount (PKR)</label>
        <input v-model.number="form.theka_amount" type="number" placeholder="e.g. 80000" class="w-full border rounded px-2 py-1 text-sm" />
      </template>
      <template v-if="form.agreement_type === 'batai'">
        <label class="block text-xs font-medium text-gray-600 mb-1">Farmer Share (%)</label>
        <input v-model.number="form.farmer_share_pct" type="number" placeholder="e.g. 60" class="w-full border rounded px-2 py-1 text-sm" />
        <label class="block text-xs font-medium text-gray-600 mb-1">Landowner Share (%)</label>
        <input v-model.number="form.landowner_share_pct" type="number" placeholder="e.g. 40" class="w-full border rounded px-2 py-1 text-sm" />
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
    const payload = { ...form, tenant_phone: auth.user.phone }
    if (payload.agreement_type !== 'theka') delete payload.theka_amount
    if (payload.agreement_type !== 'batai') { delete payload.farmer_share_pct; delete payload.landowner_share_pct }
    await land.createAgreement(payload)
  } catch (err) {
    const data = err.response?.data
    errorMessage.value = Array.isArray(data?.non_field_errors) ? data.non_field_errors[0] : (data?.message || 'Failed to submit request.')
  }
}
</script>