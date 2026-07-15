<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-1">السلام علیکم، {{ auth.user?.full_name }}</h1>
    <p class="text-sm text-gray-500 mb-6">{{ auth.user?.district }}</p>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      <div :class="['p-4 rounded shadow bg-white', community.pendingQueueCount > 0 ? 'border-2 border-amber-400' : '']">
        <p class="text-xs text-gray-500">Pending Approvals</p>
        <p class="text-2xl font-bold" :class="community.pendingQueueCount > 0 ? 'text-amber-600' : 'text-gray-800'">{{ community.pendingQueueCount }}</p>
      </div>
    </div>
    <router-link to="/numberdar/queue" class="inline-block bg-green-700 text-white px-4 py-2 rounded font-medium">
      Go to Verification Queue →
    </router-link>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useCommunityStore } from '@/stores/community.js'
const auth = useAuthStore()
const community = useCommunityStore()
onMounted(() => community.fetchQueue())
</script>