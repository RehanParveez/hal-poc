<template>
  <div class="inline-flex bg-gray-100 rounded-full p-1 gap-1 flex-wrap">
    <button v-for="tab in tabs" :key="tab.value" @click="$emit('update:modelValue', tab.value)"
      :class="['px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200',
        modelValue === tab.value ? 'bg-white text-green-800 shadow-sm' : 'text-gray-500 hover:text-gray-700']">
      {{ tab.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  tabs: { type: Array, required: true },       // [{ label, value }]
  modelValue: { type: [String, null], default: '' },
})
defineEmits(['update:modelValue'])
</script>