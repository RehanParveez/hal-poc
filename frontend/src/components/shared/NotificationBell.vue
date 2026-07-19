<template>
  <div class="relative">
    <button @click="toggleOpen" class="relative text-gray-500 hover:text-gray-800">
      <span class="text-xl">🔔</span>
      <span v-if="inbox.unreadCount > 0" :class="['absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center', badgePop ? 'animate-badge-pop' : '']">
        {{ inbox.unreadCount > 9 ? '9+' : inbox.unreadCount }}
      </span>
    </button>
    <div v-if="open" class="absolute right-0 mt-2 w-80 bg-white border rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
      <div class="flex justify-between items-center px-3 py-2 border-b">
        <p class="text-sm font-semibold">Notifications</p>
        <button @click="inbox.markAllRead()" class="text-xs text-green-700 hover:underline">Mark all read</button>
      </div>
      <div v-if="inbox.items.length === 0" class="p-4 text-sm text-gray-400 text-center">No notifications yet.</div>
      <button v-for="n in inbox.items" :key="n.id" @click="handleClick(n)"
        :class="['w-full text-left px-3 py-2 border-b text-sm hover:bg-gray-50', !n.is_read ? 'bg-green-50' : '']">
        <p class="font-medium">{{ n.subject }}</p>
        <p class="text-gray-500 text-xs mt-0.5">{{ n.message }}</p>
        <p class="text-gray-400 text-xs mt-1">{{ new Date(n.created_at).toLocaleString() }}</p>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useInboxStore } from '@/stores/inbox.js'

const inbox = useInboxStore()
const open = ref(false)
const badgePop = ref(false)

watch(() => inbox.unreadCount, (newVal, oldVal) => {
  if (newVal > oldVal) {
    badgePop.value = true
    setTimeout(() => { badgePop.value = false }, 400)
  }
})

function toggleOpen() {
  open.value = !open.value
  if (open.value) inbox.fetchMine()
}
function handleClick(n) {
  if (!n.is_read) inbox.markRead(n.id)
}
onMounted(() => inbox.fetchUnreadCount())
</script>