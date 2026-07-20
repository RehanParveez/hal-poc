<template>
  <div class="mt-8">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">{{ $t('landowner.myLandParcels') }}</h2>
      <button @click="showForm = !showForm" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">
        {{ showForm ? $t('common.cancel') : $t('landowner.registerParcel') }}
      </button>
    </div>

    <div v-if="showForm" class="bg-white p-4 rounded shadow mb-4 space-y-2">
      <input v-model="form.parcel_ref" type="text" placeholder="$t('landowner.parcelReference')" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model="form.district" type="text" placeholder="$t('common.district')" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model="form.tehsil" type="text" placeholder="$t('landowner.tehsil')" class="w-full border rounded px-2 py-1 text-sm" />
      <input v-model.number="form.total_acres" type="number" placeholder="$t('landowner.totalAcres')" class="w-full border rounded px-2 py-1 text-sm" />
      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">{{ $t('landowner.saveParcel') }}</button>
    </div>

    <div class="space-y-2">
      <div v-for="p in land.parcels" :key="p.id" class="bg-white p-3 rounded shadow flex justify-between text-sm">
        <div>
          <p class="font-medium">{{ p.parcel_ref }} — {{ p.district }}</p>
          <p class="text-gray-500">{{ p.total_acres }} acres total, {{ p.available_acres }} available</p>
        </div>
        <span v-if="p.arazi_verified" class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full self-start">{{ $t('landowner.verified') }}</span>
      </div>
      <div v-if="land.isLoading" class="text-gray-500">{{ $t('common.loading') }}</div>
      <div v-else-if="land.parcels.length === 0" class="text-gray-500">{{ $t('landowner.noParcelsYet') }}</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useLandStore } from '@/stores/land.js'

const land = useLandStore()
const showForm = ref(false)
const errorMessage = ref('')
const form = reactive({ parcel_ref: '', district: '', tehsil: '', total_acres: 0 })

onMounted(() => {
  land.fetchParcels()
})

async function submit() {
  errorMessage.value = ''
  if (!form.parcel_ref.trim() || !form.district.trim()) {
    errorMessage.value = t('landowner.errorParcelRequired')
    return
  }
  if (!form.total_acres || form.total_acres <= 0) {
    errorMessage.value = t('landowner.errorTotalAcresZero')
    return
  }
  try {
    await land.createParcel({ ...form })
    showForm.value = false
    form.parcel_ref = ''
    form.district = ''
    form.tehsil = ''
    form.total_acres = 0
  } catch (err) {
    errorMessage.value = Object.values(err.response?.data || {})[0]?.[0] || t('landowner.errorRegisterParcel')
  }
}
</script>