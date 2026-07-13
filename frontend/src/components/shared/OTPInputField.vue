<template>
  <div>
    <div class="flex gap-2 justify-center">
      <input
        v-for="(digit, i) in digits"
        :key="i"
        :ref="el => inputRefs[i] = el"
        v-model="digits[i]"
        type="text"
        inputmode="numeric"
        maxlength="1"
        :disabled="disabled"
        :class="['w-11 h-12 text-center text-lg border rounded', hasError ? 'border-red-500 text-red-600' : 'border-gray-300']"
        @input="onInput(i, $event)"
        @keydown.backspace="onBackspace(i, $event)"
      />
    </div>
    <div class="text-center mt-3 text-sm">
      <button v-if="canResend" @click="handleResend" type="button" class="text-green-700 hover:underline">Resend OTP</button>
      <span v-else class="text-gray-400">Resend in {{ timeRemaining }}s</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  hasError: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'complete', 'resend'])

const digits = reactive(['', '', '', '', '', ''])
const inputRefs = ref([])
const cooldownSeconds = Number(import.meta.env.VITE_OTP_RESEND_COOLDOWN_SECONDS || 60)
const timeRemaining = ref(cooldownSeconds)
const canResend = ref(false)
let timerId = null

function startCountdown() {
  timeRemaining.value = cooldownSeconds
  canResend.value = false
  clearInterval(timerId)
  timerId = setInterval(() => {
    timeRemaining.value -= 1
    if (timeRemaining.value <= 0) {
      canResend.value = true
      clearInterval(timerId)
    }
  }, 1000)
}

function onInput(i, event) {
  const val = event.target.value.replace(/[^0-9]/g, '')
  digits[i] = val.slice(-1)
  emit('update:modelValue', digits.join(''))
  if (val && i < 5) inputRefs.value[i + 1]?.focus()
  if (digits.every((d) => d !== '')) emit('complete', digits.join(''))
}

function onBackspace(i) {
  if (!digits[i] && i > 0) inputRefs.value[i - 1]?.focus()
}

function handleResend() {
  emit('resend')
  startCountdown()
}

onMounted(startCountdown)
onUnmounted(() => clearInterval(timerId))
defineExpose({ startCountdown })
</script>