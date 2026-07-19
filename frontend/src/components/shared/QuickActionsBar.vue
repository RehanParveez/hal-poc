<template>
  <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-2 flex flex-wrap gap-1 animate-fade-in-up">
    <button v-for="action in actions" :key="action.label" @click="action.onClick"
      class="flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-medium text-gray-700 hover:bg-green-50 hover:text-green-800 transition-colors">
      <component :is="action.icon" :size="18" />
      {{ action.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({ actions: { type: Array, required: true } })   // [{ label, icon, onClick }]
</script>