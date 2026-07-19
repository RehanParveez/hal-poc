<template>
  <div class="fixed bottom-6 right-6 z-40">
    <Transition name="modal">
      <div v-if="open" class="absolute bottom-16 right-0 w-72 bg-white rounded-2xl shadow-xl border border-gray-200 p-5">
        <p class="font-display font-semibold text-gray-900 mb-1">Need help?</p>
        <p class="text-sm text-gray-500 mb-4">Our support team is here for you, in Urdu or English.</p>
        <a href="tel:+924800000000" class="flex items-center gap-2 text-sm text-green-700 font-medium mb-2">
          <Phone :size="16" /> +92 48 0000000
        </a>
        <a href="mailto:support@hal.pk" class="flex items-center gap-2 text-sm text-green-700 font-medium">
          <Mail :size="16" /> support@hal.pk
        </a>
      </div>
    </Transition>
    <button @click="open = !open"
      class="w-14 h-14 rounded-full bg-green-700 hover:bg-green-800 text-white shadow-lg flex items-center justify-center transition-all hover:scale-105 active:scale-95">
      <component :is="open ? X : MessageCircleQuestion" :size="24" />
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { MessageCircleQuestion, X, Phone, Mail } from 'lucide-vue-next'
const open = ref(false)
</script>