<template>
  <transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="-translate-y-full opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="-translate-y-full opacity-0"
  >
    <div v-if="notify.current" dir="ltr" :class="['fixed top-0 left-0 right-0 z-50 px-4 py-3 shadow-lg', bannerClass]">
      <div class="max-w-4xl mx-auto flex items-start gap-3">
        <span class="text-xl flex-shrink-0 mt-0.5">{{ bannerIcon }}</span>
        <div class="flex-1 min-w-0">
          <p class="font-semibold text-sm">{{ bannerTitle }}</p>
          <p class="text-sm mt-0.5 opacity-90">{{ notify.current.message }}</p>

          <div
            v-if="notify.current.type === 'afo-error'"
            class="mt-2 bg-white bg-opacity-20 rounded-lg p-3 text-xs space-y-1"
          >
            <div class="flex justify-between">
              <span class="opacity-75">Category:</span>
              <span class="font-semibold capitalize">{{ notify.current.category }}</span>
            </div>
            <div class="flex justify-between">
              <span class="opacity-75">Requested Amount:</span>
              <span class="font-semibold">PKR {{ formatPKR(notify.current.requested) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="opacity-75">AFO Cap (Total):</span>
              <span class="font-semibold">PKR {{ formatPKR(notify.current.cap) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="opacity-75">Already Spent:</span>
              <span class="font-semibold">PKR {{ formatPKR(notify.current.spent) }}</span>
            </div>
            <div class="flex justify-between border-t border-white border-opacity-30 pt-1">
              <span class="font-semibold">Remaining Allowed:</span>
              <span class="font-bold">PKR {{ formatPKR(notify.current.remaining) }}</span>
            </div>
          </div>
        </div>
        <button
          @click="notify.dismissCurrent()"
          class="flex-shrink-0 text-lg opacity-70 hover:opacity-100 transition-opacity"
        >✕</button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue'
import { useNotificationsStore } from '@/stores/notifications.js'

const notify = useNotificationsStore()

const bannerClass = computed(() => {
  const type = notify.current?.type
  if (type === 'success') return 'bg-green-600 text-white'
  if (type === 'error' || type === 'afo-error') return 'bg-red-600 text-white'
  if (type === 'warning') return 'bg-amber-500 text-white'
  return 'bg-gray-700 text-white'
})

const bannerIcon = computed(() => {
  const type = notify.current?.type
  if (type === 'success') return '✓'
  if (type === 'afo-error') return '🚫'
  if (type === 'error') return '✕'
  if (type === 'warning') return '⚠'
  return 'ℹ'
})

const bannerTitle = computed(() => {
  if (notify.current?.title) return notify.current.title
  const type = notify.current?.type
  if (type === 'success') return 'Success'
  if (type === 'afo-error') return 'AFO Limit Exceeded'
  if (type === 'error') return 'Error'
  if (type === 'warning') return 'Notice'
  return 'Notice'
})

const formatPKR = (val) => {
  const num = parseFloat(val)
  if (isNaN(num)) return '—'
  return new Intl.NumberFormat('en-PK').format(Math.round(num))
}
</script>