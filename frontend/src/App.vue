<template>
  <NotificationBanner />
  <AppShell v-if="!PUBLIC_ROUTES.includes(route.path)">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
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

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>