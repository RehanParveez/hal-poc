<template>
  <div>
    <h3 class="font-bold text-gray-800 mb-2">{{ $t('credit.title') }}</h3>
    <p class="text-sm text-gray-500 mb-3">{{ $t('credit.consentIntro') }}
      Before your loan can be disbursed, your bank needs to check your credit history through eCIB and Tasdeeq.
      This information is only shared with your partner bank and HAL.
    </p>
    <label class="flex items-start gap-2 text-sm mb-2">
      <input type="checkbox" v-model="consent1" class="mt-1" />
      <span>{{ $t('credit.consent1') }}</span>
    </label>
    <label class="flex items-start gap-2 text-sm mb-2">
      <input type="checkbox" v-model="consent2" class="mt-1" />
      <span>I authorize access to my Tasdeeq credit score</span>
    </label>
    <label class="flex items-start gap-2 text-sm mb-4">
      <input type="checkbox" v-model="consent3" class="mt-1" />
      <span>I understand this check will be logged and stored per SBP regulations</span>
    </label>
    <button v-if="!otpSent" @click="handleSendOTP" :disabled="!allConsented || credit.isRequestingOTP"
      class="bg-green-700 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
      {{ credit.isRequestingOTP ? 'Sending...' : 'Send OTP' }}
    </button>
    <div v-else class="mt-3">
      <p class="text-sm text-gray-600 mb-2">Enter the 6-digit code sent to your phone:</p>
      <OTPInputField v-model="otpValue" :has-error="otpError" @complete="handleVerify" @resend="handleSendOTP" />
      <p v-if="otpError" class="text-red-600 text-xs mt-2">Incorrect or expired OTP. Please try again.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCreditStore } from '@/stores/credit.js'
import OTPInputField from '@/components/shared/OTPInputField.vue'

const props = defineProps({ loanId: { type: String, required: true } })
const emit = defineEmits(['consent-complete'])
const credit = useCreditStore()
const consent1 = ref(false), consent2 = ref(false), consent3 = ref(false)
const allConsented = computed(() => consent1.value && consent2.value && consent3.value)
const otpSent = ref(false)
const otpValue = ref('')
const otpError = ref(false)

async function handleSendOTP() {
  await credit.requestOTP(props.loanId)
  otpSent.value = true
  otpError.value = false
}
async function handleVerify(code) {
  otpError.value = false
  try {
    await credit.verifyOTP(code)
    emit('consent-complete')
  } catch (err) {
    otpError.value = true
  }
}
</script>