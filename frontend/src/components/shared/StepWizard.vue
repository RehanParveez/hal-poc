<template>
  <div>
    <div class="flex items-center justify-center mb-6">
      <template v-for="(step, i) in steps" :key="step.id">
        <div class="flex flex-col items-center">
          <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors duration-300',
           completedSteps.includes(i) ? 'bg-green-700 text-white' :
           i === currentStep ? 'bg-green-800 text-white' : 'bg-gray-200 text-gray-400']">
            <span v-if="completedSteps.includes(i)">✓</span>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <p class="text-xs mt-1 text-gray-600">{{ step.label }}</p>
        </div>
        <div v-if="i < steps.length - 1" class="w-10 h-0.5 mx-1 transition-colors duration-300"
          :class="completedSteps.includes(i) ? 'bg-green-700' : 'bg-gray-200'" />
      </template>
    </div>
    <p class="sm:hidden text-center text-sm text-gray-500 mb-3">Step {{ currentStep + 1 }} of {{ steps.length }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  steps: { type: Array, required: true },
  currentStep: { type: Number, default: 0 },
  completedSteps: { type: Array, default: () => [] },
})
defineEmits(['step-change'])
</script>