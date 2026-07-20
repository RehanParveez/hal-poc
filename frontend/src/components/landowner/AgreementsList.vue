<template>
  <div class="mt-8">
    <h2 class="text-xl font-bold mb-4">{{ $t('landowner.tenantAgreements') }}</h2>
    <button @click="showForm = !showForm" class="mb-4 bg-green-700 text-white px-3 py-1.5 rounded text-sm">
      {{ showForm ? $t('common.cancel') : $t('landowner.newAgreement') }}
    </button>
    <div v-if="showForm" class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <input v-model="form.tenant_phone" placeholder="$t('landowner.tenantPhone')" class="w-full border rounded px-2 py-1 text-sm" />
      <select v-model="form.parcel" class="w-full border rounded px-2 py-1 text-sm">
        <option value="" disabled>{{ $t('landowner.selectLandParcel') }}</option>
        <option v-for="p in availableParcels" :key="p.id" :value="p.id">
          {{ p.parcel_ref }}
        </option>
      </select>
      
      <select v-model="form.agreement_type" class="w-full border rounded px-2 py-1 text-sm">
        <option value="theka">{{ $t('farmer.theka') }}</option>
        <option value="batai">{{ $t('farmer.batai') }}</option>
      </select>

    <div v-if="form.agreement_type === 'batai'" class="space-y-2">
      <input v-model.number="form.farmer_share_pct" type="number" placeholder="Farmer Share %" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.landowner_share_pct" type="number" placeholder="Landowner Share %" class="w-full border rounded px-2 py-1 text-sm" />
    </div>

    <div v-if="form.agreement_type === 'theka'" class="space-y-2">
      <input v-model.number="form.theka_amount" type="number" placeholder="Theka Amount (PKR)" class="w-full border rounded px-2 py-1 text-sm" />
    </div>
      
      <select v-model="form.season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="" disabled selected>{{ $t('farmer.selectSeason') }}</option>
        <option value="Kharif">{{ $t('farmer.kharif') }}</option>
        <option value="Rabi">{{ $t('farmer.rabi') }}</option>
      </select>
      <input v-model.number="form.leased_acres" type="number" :placeholder="$t('farmer.leasedAcres')" class="w-full border rounded px-2 py-1 text-sm" />
      
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm w-full">{{ $t('landowner.saveAgreement') }}</button>
    </div>
    <div class="space-y-2">
      <div v-for="a in land.agreements" :key="a.id" class="bg-white p-4 rounded shadow">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-semibold">{{ a.tenant_name }} — {{ a.parcel_ref }}</p>
            <p class="text-sm text-gray-500">{{ $t('farmer.' + a.agreement_type) }} — {{ a.leased_acres }} {{ $t('farmer.acresAppliedFor') }} — {{ $t('farmer.' + a.season.toLowerCase()) }}</p>
            <p v-if="a.agreement_type === 'theka'" class="text-sm text-gray-500">{{ $t('landowner.rent') }}: PKR {{ a.theka_amount }}</p>
            <p v-else class="text-sm text-gray-500">{{ $t('farmer.farmerShare') }} {{ a.farmer_share_pct }}% / {{ $t('farmer.landownerShare') }} {{ a.landowner_share_pct }}%</p>
          </div>
          <StatusBadge :status="a.status" />
        </div>

        <div v-if="a.status === 'pending'" class="mt-3 flex gap-2">
          <button @click="handleApprove(a.id)" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">{{ $t('common.approve') }}</button>
          <button @click="handleReject(a.id)" class="bg-red-600 text-white px-3 py-1.5 rounded text-sm">{{ $t('common.reject') }}</button>
        </div>
      </div>
      <p v-if="land.agreements.length === 0" class="text-gray-500">{{ $t('landowner.noAgreementsYet') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useLandStore } from '@/stores/land.js'
import { useNotificationsStore } from '@/stores/notifications.js'
import StatusBadge from '@/components/shared/StatusBadge.vue'

const land = useLandStore()
const notify = useNotificationsStore()
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
  if (!form.tenant_phone.trim() || !form.parcel || !form.season) {
    notify.showError(t('landowner.errorAgreementRequired'))
    return
  }
  if (!form.leased_acres || form.leased_acres <= 0) {
    notify.showError(t('landowner.errorLeasedAcresZero'))
    return
  }
  if (form.agreement_type === 'theka' && (!form.theka_amount || form.theka_amount <= 0)) {
    notify.showError(t('landowner.errorThekaAmountZero'))
    return
  }
  try {
    await land.createAgreement({ ...form })
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
  } catch (error) {
    notify.showError(error.response?.data?.error ?? t('landowner.errorCreateAgreement'))
  }
}

async function handleApprove(id) {
  try {
    await land.approveAgreement(id)
  } catch (error) {
    notify.showError(error.response?.data?.error ?? t('landowner.errorApproveAgreement'))
  }
}

function handleReject(id) {
  const reason = window.prompt('Rejection reason:')
  if (reason) {
    land.rejectAgreement(id, reason).catch((error) => {
      notify.showError(error.response?.data?.error ?? t('landowner.errorRejectAgreement'))
    })
  }
}
</script>