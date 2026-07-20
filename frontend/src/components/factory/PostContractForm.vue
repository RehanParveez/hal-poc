<template>
  <div class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-3">{{ $t('factory.postNewContract') }}</h2>
    <div class="space-y-2">
      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('farmer.selectCrop') }}</label>
      <select v-model="form.crop" class="w-full border rounded px-2 py-1 text-sm">
        <option value="">{{ $t('farmer.selectCrop') }}</option>
        <option v-for="c in crops.cropTypes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
      </select>

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('factory.requiredQuantity') }}</label>
      <input v-model.number="form.required_kg" type="number" placeholder="$t('factory.requiredQuantityPlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('factory.basePricePerKg') }}</label>
      <input v-model.number="form.base_price_per_kg" type="number" :placeholder="$t('factory.basePricePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('factory.paymentDeferDays') }}</label>
      <input v-model.number="form.payment_defer_days" type="number" :placeholder="$t('factory.paymentDeferPlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('factory.qualityGradeExpected') }}</label>
      <input v-model="form.quality_grade_expected" type="text" :placeholder="$t('factory.qualityGradePlaceholder')" class="w-full border rounded px-2 py-1 text-sm" />

      <label class="block text-xs font-medium text-gray-600 mb-1">{{ $t('factory.deliveryDeadline') }}</label>
      <input v-model="form.delivery_deadline" type="date" class="w-full border rounded px-2 py-1 text-sm" />

      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button @click="submit" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">{{ $t('factory.postContractBtn') }}</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useCropsStore } from '@/stores/crops.js'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const contracts = useContractsStore()
const crops = useCropsStore()
const errorMessage = ref('')
const form = reactive({ crop: '', required_kg: 0, base_price_per_kg: 0, payment_defer_days: 20, quality_grade_expected: 'Grade A', delivery_deadline: '' })

onMounted(async () => {
  if (crops.cropTypes.length === 0) {
    await crops.fetchCropTypes()
  }
})

async function submit() {
  errorMessage.value = ''
  if (!form.crop) { errorMessage.value = t('factory.errorSelectCrop'); return }
  if (!form.required_kg || form.required_kg <= 0) { errorMessage.value = t('factory.errorRequiredQuantity'); return }
  if (!form.base_price_per_kg || form.base_price_per_kg <= 0) { errorMessage.value = t('factory.errorBasePrice'); return }
  if (!form.payment_defer_days || form.payment_defer_days < 1 || form.payment_defer_days > 30) { errorMessage.value = t('factory.errorPaymentDefer'); return }
  if (!form.delivery_deadline) { errorMessage.value = t('factory.errorDeliveryDeadline'); return }
  try {
    await contracts.createContract({ ...form })
  } catch (err) {
    const data = err.response?.data
    errorMessage.value = Object.values(data || {})[0]?.[0] || t('factory.errorPostContract')
  }
}
</script>