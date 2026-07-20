<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">{{ $t('farmer.requestTenantAgreement') }}</h2>
    <div class="space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.selectParcel') }}</label>
      <select v-model="form.parcel" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('farmer.selectParcel') }}</option>
        <option v-for="p in land.parcels" :key="p.id" :value="p.id">{{ p.parcel_ref }} — {{ p.district }} ({{ p.available_acres }} {{ $t('farmer.acresAppliedFor') }} {{ $t('landowner.available') }})</option>
      </select>

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.agreementType') }}</label>
      <select v-model="form.agreement_type" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('common.select') }}</option>
        <option value="theka">{{ $t('farmer.theka') }}</option>
        <option value="batai">{{ $t('farmer.batai') }}</option>
      </select>

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.leasedAcres') }}</label>
      <input v-model.number="form.leased_acres" type="number" placeholder="$t('farmer.acresPlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      <p v-if="acreageExceedsAvailable" class="text-xs text-red-600">{{ $t('farmer.errorAcreageExceeds') }}</p>

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.season') }}</label>
      <select v-model="form.season" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('common.select') }}</option>
        <option value="kharif">{{ $t('farmer.kharif') }}</option>
        <option value="rabi">{{ $t('farmer.rabi') }}</option>
      </select>

      <template v-if="form.agreement_type === 'theka'">
        <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.thekaAmount') }}</label>
        <input v-model.number="form.theka_amount" type="number" min="0" step="0.01" placeholder="$t('farmer.thekaAmountPlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
      </template>

      <template v-if="form.agreement_type === 'batai'">
        <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.farmerShare') }}</label>
        <input v-model.number="form.farmer_share_pct" type="number" min="0" max="100" step="0.01" placeholder="$t('farmer.farmerSharePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
        <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.landownerShare') }}</label>
        <input v-model.number="form.landowner_share_pct" type="number" min="0" max="100" step="0.01" placeholder="$t('farmer.landownerSharePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />
        <p v-if="!bataiSharesValid" class="text-xs text-red-600">{{ $t('farmer.errorBataiShares') }}</p>
      </template>

      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" :disabled="isSubmitting || !isFormValid" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">
        {{ isSubmitting ? $t('farmer.submitting') : $t('farmer.submitApplication') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch } from 'vue'
import { useLandStore } from '@/stores/land.js'
import { useAuthStore } from '@/stores/auth.js'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const land = useLandStore()
const auth = useAuthStore()
const errorMessage = ref('')
const isSubmitting = ref(false)

function initialForm() {
  return { parcel: '', agreement_type: '', leased_acres: 0, season: '', theka_amount: 0, farmer_share_pct: 0, landowner_share_pct: 0 }
}

const form = reactive(initialForm())
watch(() => land.parcels, (newParcels) => {
  if (newParcels && newParcels.length > 0 && !form.parcel) {
    form.parcel = newParcels[0].id
  }
}, { immediate: true })

onMounted(() => {
  land.fetchParcels()
})

const selectedParcel = computed(() => land.parcels.find((p) => p.id === form.parcel))

const acreageExceedsAvailable = computed(() => {
  if (!selectedParcel.value || !form.leased_acres) return false
  return Number(form.leased_acres) > Number(selectedParcel.value.available_acres)
})

const bataiSharesValid = computed(() => {
  const sum = Number(form.farmer_share_pct) + Number(form.landowner_share_pct)
  return Math.abs(sum - 100) <= 0.01
})

const isFormValid = computed(() => {
  if (!form.parcel || !form.agreement_type || !form.season) return false
  if (!form.leased_acres || Number(form.leased_acres) <= 0) return false
  if (acreageExceedsAvailable.value) return false
  if (form.agreement_type === 'theka' && (!form.theka_amount || Number(form.theka_amount) <= 0)) return false
  if (form.agreement_type === 'batai' && !bataiSharesValid.value) return false
  return true
})

async function submit() {
  if (!isFormValid.value) return
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const payload = { ...form, tenant_phone: auth.user.phone }
    if (payload.agreement_type !== 'theka') delete payload.theka_amount
    if (payload.agreement_type !== 'batai') { delete payload.farmer_share_pct; delete payload.landowner_share_pct }
    await land.createAgreement(payload)
    Object.assign(form, initialForm())
  } catch (err) {
    const data = err.response?.data
    errorMessage.value = Array.isArray(data?.non_field_errors) ? data.non_field_errors[0] : (data?.message || t('farmer.errorSubmitRequest'))
  } finally {
    isSubmitting.value = false
  }
}
</script>