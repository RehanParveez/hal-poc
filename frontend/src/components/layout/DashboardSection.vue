<template>
  <section :id="id" :class="['w-full', toneClasses]">
    <div class="content-container py-12 md:py-16">
      <div v-if="eyebrow || title" class="mb-8 max-w-2xl">
        <p v-if="eyebrow" class="text-xs font-semibold text-green-700 uppercase tracking-wider mb-2">{{ eyebrow }}</p>
        <h2 v-if="title" class="text-2xl md:text-3xl font-display font-semibold text-gray-900">{{ title }}</h2>
        <p v-if="description" class="text-sm text-gray-600 mt-2">{{ description }}</p>
      </div>
      <slot />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: { type: String, default: undefined },
  eyebrow: { type: String, default: '' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  tone: { type: String, default: 'default' },
})

const toneClasses = computed(() => ({
  default: 'bg-gray-50',
  tint: 'bg-green-50/60 border-y border-green-100',
  white: 'bg-white border-y border-gray-100',
}[props.tone] || 'bg-gray-50'))
</script>