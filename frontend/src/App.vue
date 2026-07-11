<template>
  <NotificationBanner />
  <AppShell v-if="!PUBLIC_ROUTES.includes(route.path)">
    <router-view />
  </AppShell>
  <router-view v-else />
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppShell from '@/components/layout/AppShell.vue'
import NotificationBanner from '@/components/shared/NotificationBanner.vue'

const PUBLIC_ROUTES = ['/login', '/register']
const route = useRoute()
</script>