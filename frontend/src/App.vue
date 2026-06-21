<template>
 <AppShell v-if="route.path !== '/login'">
  <router-view />
 </AppShell>
 <router-view v-else />
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppShell from '@/components/layout/AppShell.vue'

const route = useRoute()
</script>