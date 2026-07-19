<template>
  <div class="w-full relative overflow-hidden text-white" style="background: linear-gradient(135deg, #1c3a26 0%, #295c39 45%, #0e2015 100%);">
  <div class="absolute inset-0 mesh-hero"></div>
  <div class="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-gold-400/10 blur-3xl"></div>
  <div class="absolute -bottom-32 -left-16 w-80 h-80 rounded-full bg-green-400/10 blur-3xl"></div>
    <div class="content-container py-12 md:py-16 relative z-10">
      <div class="flex items-start justify-between flex-wrap gap-6">
        <div>
          <p class="text-green-200 text-sm">{{ eyebrow }}</p>
          <h1 class="text-3xl md:text-4xl font-display font-semibold mt-1">{{ title }}</h1>
          <p v-if="subtitle" class="text-green-100/80 text-sm mt-2 max-w-xl">{{ subtitle }}</p>
        </div>
        <slot name="action" />
      </div>
      <div v-for="stat in stats" :key="stat.label" class="bg-white/10 backdrop-blur-sm rounded-xl px-4 py-4 border border-white/10 animate-fade-in-up">
       <component :is="stat.icon" v-if="stat.icon" :size="18" class="text-gold-400 mb-2" />
        <p class="text-2xl font-display font-semibold tabular-nums">{{ stat.value }}</p>
          <p class="text-xs text-green-200 uppercase tracking-wide mt-0.5">{{ stat.label }}</p>
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