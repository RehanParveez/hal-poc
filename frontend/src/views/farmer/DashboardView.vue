<template>
  <div class="p-8">
    <EscrowDashboardView v-if="auth.isLoggedIn" />
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import EscrowDashboardView from './EscrowDashboardView.vue'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>