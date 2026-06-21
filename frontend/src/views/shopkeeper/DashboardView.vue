<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold">Shopkeeper Dashboard</h1>
    <p class="text-gray-600 mt-2">Logged in as {{ auth.user?.full_name }} ({{ auth.user?.role }})</p>
    <button @click="handleLogout" class="mt-4 bg-gray-800 text-white px-4 py-2 rounded">Logout</button>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>