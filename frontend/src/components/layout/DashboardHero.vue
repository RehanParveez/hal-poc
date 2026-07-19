<template>
  <div class="w-full text-white relative overflow-hidden mesh-hero">
    <div class="content-container py-10 md:py-14 relative z-10">
      <div class="flex items-start justify-between flex-wrap gap-4">
        <div>
          <p class="text-green-200 text-sm">{{ eyebrow }}</p>
          <h1 class="text-3xl md:text-4xl font-display font-semibold mt-1">{{ title }}</h1>
          <p v-if="subtitle" class="text-green-100/80 text-sm mt-2 max-w-xl">{{ subtitle }}</p>
        </div>
        <slot name="action" />
      </div>
      <div v-if="stats?.length" class="flex flex-wrap gap-3 mt-6">
        <div v-for="stat in stats" :key="stat.label" class="bg-white/10 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/10 animate-fade-in-up">
          <p class="text-2xl font-display font-semibold tabular-nums">{{ stat.value }}</p>
          <p class="text-xs text-green-200 uppercase tracking-wide mt-0.5">{{ stat.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  stats: { type: Array, default: () => [] },
})
</script>