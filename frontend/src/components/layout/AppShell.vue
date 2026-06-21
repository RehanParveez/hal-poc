<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <AppSidebar />
    <div class="flex flex-col flex-1 overflow-hidden">
      <AppTopbar />
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
</script>