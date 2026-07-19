<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <AppSidebar />
    <div class="flex flex-col flex-1 overflow-hidden">
      <AppTopbar />
      <main class="flex-1 overflow-y-auto">
        <div class="flex-1"><slot /></div>
        <AppFooter />
      </main>
    </div>
    <HelpFab />
  </div>
</template>


<script setup>
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
import AppFooter from './AppFooter.vue'
import HelpFab from '@/components/shared/HelpFab.vue'
</script>